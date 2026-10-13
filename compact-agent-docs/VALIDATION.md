# Validation evidence

## Status: review, 2026-09-21

Version 1.2 was authored and evaluated in a Codex session; the exact hosted model build is not exposed. The local environment used Linux x86_64, Python 3.10.12, and Git 2.34.1. This is not a cross-client certification and no general compression percentage is published.

## Repeatable checks

From the repository root:

```bash
python3 -B -m unittest discover -s compact-agent-docs/tests -v
python3 compact-agent-docs/scripts/doc_guard.py inventory compact-agent-docs
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" compact-agent-docs
```

Seven helper tests cover discovery of standard, linked, unlinked, business, and custom Markdown; default dependency-tree exclusion; missing targets and broken local links; ignoring links shown only as code examples; strict failure when commands, URLs, link targets, or numeric values disappear; and the explicit refusal to claim semantic equivalence after a structural check.

For the no-argument default, `inventory . --json` was run from this repository root. It found 24 Markdown documents with no broken local links and classified `AGENTS.md`, all five `SKILL.md` entrypoints, and their agent references as agent-facing while keeping ordinary `README.md` files and other project/custom documents distinct. A manual decision-path review confirmed that this non-empty set proceeds without asking for a path, while the documented empty and ambiguous cases stop for direction after reporting discovery evidence. This validates instruction routing, not live automatic invocation in every client.

A synthetic approved checkout PRD exercised the Apply workflow. The compacted fixture retained status, owner, target date, goal, four identified requirements, acceptance conditions, risk, and open question while removing repeated prose. It decreased from 1,084 to 772 characters (28.8%); bidirectional manual review and strict structural/literal comparison passed. An intentionally unsafe 194-character variant dropped the date and `5000 USD` threshold; strict comparison failed and reported the missing numeric values. This fixture demonstrates the guardrails, not an expected compression rate for other documents.

## Scenario review

The instructions were reviewed against these representative cases:

| Case | Expected behavior |
| --- | --- |
| Invoke `$compact-agent-docs` with no arguments | Resolve the current repository root, inventory before asking, state the inferred agent-document scope, and Apply to clearly agent-facing files without expanding to all Markdown. |
| Find no standard agent-facing file during bare invocation | Report the searched root and likely custom candidates, then ask for direction instead of guessing or asking for a path before discovery. |
| Compact a named `AGENTS.md` | Apply only to that file and its direct dependencies; preserve scope, force, commands, and exceptions. |
| Audit all repository docs | Inventory all in-scope Markdown before following links; include unlinked custom files; do not edit. |
| Compact a PRD and policy | Preserve requirements, criteria, owners, dates, decisions, risks, approvals, and unresolved questions; flag domain-sensitive equivalence. |
| Encounter license or generated API docs | Classify as exact-sensitive or generated and default to audit-only. |
| Request a fixed 50% reduction | Refuse to sacrifice meaning; report the safe reduction actually achieved or retain the source. |
| Find contradictory requirements | Preserve and report both rather than silently selecting one. |
| Reword a command or remove a link | Flag the protected-literal difference for review. |
| Ask for a summary that may omit detail | Do not select this skill solely for ordinary summarization. |

## Remaining gaps

Readiness recheck on 2026-10-13: the local and copied standalone skill passed the bundled validator and all seven helper tests; metadata/UI checks and standalone inventory passed. Repository inventory found 24 Markdown documents with no reported broken local file links, and `git diff --check` passed. Targeted temporary fixtures also reproduced three helper limitations: mismatched code-fence markers can pass strict comparison, valid angle-bracket link paths containing spaces can be reported as broken, and `.github/instructions/*.instructions.md` files are classified as project rather than agent documents. These remain unfixed; manual structural and classification review is required. Version 1.2 remains suitable for supervised use at stage `review`.

Actual automatic invocation, installation, and runtime behavior have not been tested in Claude Code, Cursor, or GitHub Copilot. The workflow has not yet been forward-tested on a large real-world documentation repository or reviewed by legal, compliance, product, and policy domain owners. The helper does not parse full Markdown ASTs, validate remote URLs or heading anchors, honor every client-specific import syntax, calculate model tokens, or prove natural-language equivalence. Windows and macOS execution have not been tested. These gaps keep the lifecycle stage at `review`.

The bundled skill-creator validator, metadata/UI assertions, local-link inventory, Python syntax, seven unit tests, unresolved-placeholder search, and whitespace checks passed. A copied standalone folder passed its validator, seven tests, and inventory with no broken local links. Its README is self-contained, has no repository-relative setup or license dependency, and links to the official GNU GPLv3 page checked on 2026-09-21. Version 1.2 also received manual reviews of the dependency contract and no-argument decision path: Python and Git remain optional, no installation is authorized, and discovery now precedes any request for a path. The standalone `skills-ref` validator was unavailable. No live client or dependency installation occurred.
