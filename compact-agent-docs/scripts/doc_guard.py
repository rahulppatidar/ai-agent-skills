#!/usr/bin/env python3
"""Inventory Markdown and flag structural risks between original and compacted files."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import sys
from typing import Iterable, Optional


MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdc"}
EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    "target",
    "out",
    "__pycache__",
}
AGENT_NAMES = {
    "agents.md",
    "agents.override.md",
    "claude.md",
    "claude.local.md",
    "gemini.md",
    "copilot-instructions.md",
    "skill.md",
}
PROJECT_NAMES = {
    "readme.md",
    "contributing.md",
    "architecture.md",
    "development.md",
    "security.md",
    "support.md",
    "governance.md",
    "code_of_conduct.md",
    "code-of-conduct.md",
    "changelog.md",
    "roadmap.md",
}
EXACT_SENSITIVE_TERMS = {
    "license",
    "legal",
    "terms",
    "privacy",
    "compliance",
    "regulatory",
    "audit",
}
BUSINESS_TERMS = {
    "prd",
    "brd",
    "requirement",
    "specification",
    "proposal",
    "policy",
    "procedure",
    "sop",
    "runbook",
    "playbook",
    "strategy",
    "roadmap",
    "plan",
    "brief",
    "charter",
    "decision",
    "adr",
    "rfc",
    "meeting",
    "research",
    "onboarding",
    "risk",
}

INLINE_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
IMPORT_RE = re.compile(r"(?m)^\s*@([^\s]+\.(?:md|markdown|mdc))\s*$", re.IGNORECASE)
URL_RE = re.compile(r"(?:https?|mailto):[^\s)>]+")
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
FENCE_RE = re.compile(r"(?ms)^(?P<marker>```|~~~)[^\n]*\n.*?^(?P=marker)\s*$")
NUMBER_RE = re.compile(r"(?<![\w.-])[+-]?\d+(?:[.,]\d+)*(?:%|[A-Za-z]+)?(?![\w.-])")
MODAL_RE = re.compile(
    r"\b(must not|must|shall not|shall|required|prohibited|should not|should|may not|may|never|only)\b",
    re.IGNORECASE,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def classify(path: Path) -> str:
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    stem_terms = {term for term in re.split(r"[^a-z0-9]+", path.stem.lower()) if term}
    if stem_terms & EXACT_SENSITIVE_TERMS or name in {"license.md", "privacy.md"}:
        return "exact-sensitive"
    skill_reference = "references" in parts and any(
        (parent / "SKILL.md").is_file() for parent in path.parents
    )
    if name in AGENT_NAMES or parts & {".agents", ".claude", ".cursor"} or skill_reference:
        return "agent"
    if name in PROJECT_NAMES:
        return "project"
    if stem_terms & BUSINESS_TERMS:
        return "business"
    if "docs" in parts or ".github" in parts:
        return "project"
    return "custom"


def iter_documents(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in MARKDOWN_SUFFIXES:
            yield root
        return
    for current, directories, files in os.walk(root, followlinks=False):
        directories[:] = sorted(d for d in directories if d not in EXCLUDED_DIRS)
        for filename in sorted(files):
            path = Path(current) / filename
            if path.suffix.lower() in MARKDOWN_SUFFIXES:
                yield path


def clean_link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target and not target.startswith(("http://", "https://", "mailto:")):
        target = target.split(" ", 1)[0]
    return target


def extract_targets(text: str) -> list[str]:
    without_fences = FENCE_RE.sub("", text)
    searchable = INLINE_CODE_RE.sub("", without_fences)
    raw_targets = []
    raw_targets.extend(INLINE_LINK_RE.findall(searchable))
    raw_targets.extend(REFERENCE_LINK_RE.findall(searchable))
    raw_targets.extend(WIKI_LINK_RE.findall(searchable))
    raw_targets.extend(IMPORT_RE.findall(searchable))
    return [clean_link_target(target) for target in raw_targets]


def resolve_local_target(source: Path, target: str) -> Optional[Path]:
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return None
    without_anchor = target.split("#", 1)[0].split("?", 1)[0]
    if not without_anchor:
        return None
    candidate = (source.parent / without_anchor).resolve()
    if candidate.exists():
        return candidate
    if candidate.suffix == "":
        markdown_candidate = candidate.with_suffix(".md")
        if markdown_candidate.exists():
            return markdown_candidate
    return candidate


def metrics(text: str) -> dict[str, int]:
    return {
        "bytes": len(text.encode("utf-8")),
        "characters": len(text),
        "words": len(re.findall(r"\S+", text)),
        "lines": len(text.splitlines()),
    }


def inventory(root: Path) -> dict[str, object]:
    if not root.exists():
        raise FileNotFoundError(f"target does not exist: {root}")
    root = root.resolve()
    documents = []
    known_paths = {path.resolve() for path in iter_documents(root)}
    inbound = Counter()

    for path in sorted(known_paths):
        text = read_text(path)
        targets = extract_targets(text)
        local_links = []
        broken_links = []
        for target in targets:
            resolved = resolve_local_target(path, target)
            if resolved is None:
                continue
            display = str(resolved)
            exists = resolved.exists()
            local_links.append({"target": target, "resolved": display, "exists": exists})
            if exists:
                inbound[resolved] += 1
            else:
                broken_links.append(target)
        try:
            relative = str(path.relative_to(root if root.is_dir() else root.parent))
        except ValueError:
            relative = str(path)
        documents.append(
            {
                "path": relative,
                "role": classify(path),
                "metrics": metrics(text),
                "outbound_local_links": local_links,
                "broken_local_links": broken_links,
                "inbound_links": 0,
            }
        )

    by_resolved = {}
    for path in known_paths:
        try:
            key = str(path.relative_to(root if root.is_dir() else root.parent))
        except ValueError:
            key = str(path)
        by_resolved[key] = inbound[path]
    for document in documents:
        document["inbound_links"] = by_resolved.get(document["path"], 0)

    return {
        "root": str(root),
        "document_count": len(documents),
        "documents": documents,
    }


def fenced_balance(text: str) -> bool:
    markers = re.findall(r"(?m)^\s*(```|~~~)", text)
    return len(markers) % 2 == 0


def frontmatter_closed(text: str) -> bool:
    if not text.startswith("---\n"):
        return True
    return re.match(r"(?s)^---\n.*?\n---(?:\n|$)", text) is not None


def extracted_literals(text: str) -> dict[str, Counter[str]]:
    return {
        "urls": Counter(URL_RE.findall(text)),
        "inline_code": Counter(INLINE_CODE_RE.findall(text)),
        "fenced_blocks": Counter(match.group(0).strip() for match in FENCE_RE.finditer(text)),
        "link_targets": Counter(extract_targets(text)),
        "numbers": Counter(NUMBER_RE.findall(text)),
        "modal_terms": Counter(term.lower() for term in MODAL_RE.findall(text)),
    }


def counter_delta(before: Counter[str], after: Counter[str]) -> dict[str, list[str]]:
    removed = list((before - after).elements())
    added = list((after - before).elements())
    return {"removed": sorted(removed), "added": sorted(added)}


def compare(before_path: Path, after_path: Path) -> tuple[dict[str, object], bool]:
    before = read_text(before_path)
    after = read_text(after_path)
    before_metrics = metrics(before)
    after_metrics = metrics(after)
    before_literals = extracted_literals(before)
    after_literals = extracted_literals(after)
    literal_deltas = {
        key: counter_delta(value, after_literals[key]) for key, value in before_literals.items()
    }
    structural = {
        "after_fences_balanced": fenced_balance(after),
        "after_frontmatter_closed": frontmatter_closed(after),
    }
    high_risk_keys = {"urls", "inline_code", "fenced_blocks", "link_targets", "numbers"}
    high_risk_removed = {
        key: sorted(item for item in before_literals[key] if after_literals[key][item] == 0)
        for key in sorted(high_risk_keys)
        if any(after_literals[key][item] == 0 for item in before_literals[key])
    }
    strict_ok = all(structural.values()) and not high_risk_removed
    result = {
        "before": str(before_path.resolve()),
        "after": str(after_path.resolve()),
        "metrics": {
            "before": before_metrics,
            "after": after_metrics,
            "delta": {
                key: after_metrics[key] - before_metrics[key] for key in before_metrics
            },
        },
        "structural": structural,
        "literal_deltas": literal_deltas,
        "high_risk_removed": high_risk_removed,
        "strict_checks_passed": strict_ok,
        "semantic_equivalence_proven": False,
    }
    return result, strict_ok


def print_inventory_human(report: dict[str, object]) -> None:
    print(f"Root: {report['root']}")
    print(f"Documents: {report['document_count']}")
    for document in report["documents"]:
        metric = document["metrics"]
        print(
            f"{document['role']:15} {metric['characters']:8} chars "
            f"in:{document['inbound_links']:2} out:{len(document['outbound_local_links']):2} "
            f"{document['path']}"
        )
        for target in document["broken_local_links"]:
            print(f"  broken: {target}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory_parser = subparsers.add_parser("inventory", help="inventory Markdown documents")
    inventory_parser.add_argument("root", type=Path)
    inventory_parser.add_argument("--json", action="store_true", help="emit JSON")

    compare_parser = subparsers.add_parser("compare", help="compare original and compacted files")
    compare_parser.add_argument("before", type=Path)
    compare_parser.add_argument("after", type=Path)
    compare_parser.add_argument("--strict", action="store_true", help="fail on structural or protected-literal loss")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "inventory":
        report = inventory(args.root)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print_inventory_human(report)
        return 0

    report, strict_ok = compare(args.before, args.after)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.strict and not strict_ok:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError) as error:
        print(f"doc_guard: {error}", file=sys.stderr)
        raise SystemExit(2)
