#!/usr/bin/env python3
"""Offline Gitleaks scans with metadata-only JSON and explicit failure states.

SPDX-License-Identifier: GPL-3.0-only
Copyright (C) 2026 Rahul Patidar
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


class Incomplete(Exception):
    """Safe, fixed diagnostic text; never include subprocess output."""


def run(command, cwd, timeout):
    try:
        return subprocess.run(
            command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        raise Incomplete("Command timed out; scan coverage is incomplete.") from None
    except OSError:
        raise Incomplete("Cannot execute the required tool; check installation and permissions.") from None


def git(args, cwd, timeout):
    result = run(["git", *args], cwd, timeout)
    if result.returncode:
        raise Incomplete("Git check failed; confirm repository access and Git availability.")
    return result.stdout


def emit(status, code, scope, **fields):
    print(json.dumps({"status": status, "scope": scope, **fields}, ensure_ascii=True))
    return code


def push_tips(stream, cwd, timeout):
    """Consume Git's pre-push protocol, never shell-interpolate ref names."""
    tips = set()
    for line in stream:
        fields = line.split()
        if len(fields) != 4:
            raise Incomplete("Invalid pre-push input; invoke this mode from a native Git hook.")
        local_oid, remote_oid = fields[1], fields[3]
        if (not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", local_oid)
                or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", remote_oid)
                or len(local_oid) != len(remote_oid)):
            raise Incomplete("Invalid object IDs in pre-push input.")
        if set(local_oid) == {"0"}:
            continue  # Deletion sends no new content.
        resolved = git(["rev-parse", "--verify", local_oid + "^{commit}"], cwd, timeout).strip()
        if not re.fullmatch(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})", resolved):
            raise Incomplete("Push target is not a locally available commit or commit tag.")
        tips.add(resolved.decode("ascii"))
    return sorted(tips)


def scan(args):
    target = Path(args.path).resolve()
    if not target.exists() or not (target.is_dir() or target.is_file()):
        raise Incomplete("Target must be an existing file or directory.")
    cwd = target if target.is_dir() else target.parent
    executable = shutil.which(args.gitleaks)
    if not executable:
        raise Incomplete("Gitleaks is unavailable; install it or provide --gitleaks.")
    executable = str(Path(executable).resolve())
    version = run([executable, "version"], cwd, args.timeout)
    match = re.fullmatch(rb"v?(8\.(\d+)\.\d+)\s*", version.stdout)
    if version.returncode or not match or int(match.group(2)) < 19:
        raise Incomplete("Use a released Gitleaks 8.19+ binary in the 8.x series.")
    tool_version = match.group(1).decode("ascii")

    index_before = None
    tips = []
    if args.scope != "files":
        if not target.is_dir():
            raise Incomplete("Git scanning modes require a repository directory.")
        root = git(["rev-parse", "--show-toplevel"], cwd, args.timeout)
        target = Path(os.fsdecode(root.rstrip(b"\r\n")))
        cwd = target
        if args.scope == "pre-push":
            if sys.stdin.isatty():
                raise Incomplete("Pre-push mode requires Git hook input on stdin.")
            tips = push_tips(sys.stdin, cwd, args.timeout)
            if not tips:
                return emit("nothing_to_scan", 3, args.scope, tool_version=tool_version,
                            reason="No non-deletion push updates supplied.")
        if args.scope == "staged":
            if git(["ls-files", "--unmerged", "-z"], cwd, args.timeout):
                raise Incomplete("Resolve index conflicts before scanning staged changes.")
            index_before = git(["ls-files", "--stage", "-z"], cwd, args.timeout)
            changed = git(
                ["diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z", "--"],
                cwd, args.timeout,
            )
            if not changed:
                return emit("nothing_to_scan", 3, args.scope, tool_version=tool_version,
                            reason="No staged additions or modifications.")
        else:
            if git(["rev-parse", "--is-shallow-repository"], cwd, args.timeout).strip() == b"true":
                raise Incomplete("Shallow history; obtain the intended history before a history audit.")
            if args.scope == "history" and not git(["rev-list", "--all", "--max-count=1"], cwd, args.timeout).strip():
                return emit("nothing_to_scan", 3, args.scope, tool_version=tool_version,
                            reason="No reachable commits in available local refs.")

    command = [executable, "dir" if args.scope == "files" else "git"]
    if args.scope == "staged":
        command += ["--pre-commit", "--staged"]
    elif args.scope == "history":
        command += ["--log-opts=--all --full-history -m"]
    elif args.scope == "pre-push":
        # Full ancestry avoids trusting a missing/stale remote base, and covers
        # new branches, tags, force pushes, and secrets removed before the tip.
        command += ["--log-opts=--full-history -m " + " ".join(tips)]
    if args.config:
        config = Path(args.config).resolve()
        if not config.is_file():
            raise Incomplete("The supplied scanner configuration does not exist.")
        command += ["--config", str(config)]
    command += [
        "--redact=100", "--no-banner", "--no-color", "--log-level=error",
        "--exit-code=23", "--report-format=json", "--report-path=-", str(target),
    ]
    result = run(command, cwd, args.timeout)
    # A distinct finding code separates detection from execution/config errors.
    # Error-level diagnostics also invalidate an otherwise successful exit.
    if result.returncode not in (0, 23) or result.stderr.strip():
        raise Incomplete("Scanner failed or emitted errors; check version, configuration, and target access. Raw diagnostics withheld.")
    try:
        findings = json.loads(result.stdout)
    except (ValueError, UnicodeError):
        raise Incomplete("Scanner returned an invalid report; no clean result can be established.") from None
    if not isinstance(findings, list):
        raise Incomplete("Scanner report is not a findings list.")
    locations = []
    for item in findings:
        if not isinstance(item, dict):
            raise Incomplete("Scanner report contains an invalid finding.")
        file, line, rule = item.get("File"), item.get("StartLine"), item.get("RuleID")
        commit = item.get("Commit", "")
        if (not isinstance(file, str) or type(line) is not int or line < 1
                or not isinstance(rule, str) or not isinstance(commit, str)
                or (commit and not re.fullmatch(r"[0-9a-f]{40,64}", commit))):
            raise Incomplete("Scanner report has invalid location metadata.")
        # Explicit allowlist: Match, Secret, Description, author, email, and
        # other source/context fields must never be forwarded to the agent.
        locations.append({"file": file, "line": line, "rule": rule, "commit": commit})
    if bool(locations) != (result.returncode == 23):
        raise Incomplete("Scanner exit status and report disagree.")
    if index_before is not None:
        if git(["ls-files", "--stage", "-z"], cwd, args.timeout) != index_before:
            raise Incomplete("Git index changed during the scan; rerun against the intended staged content.")
    return emit(
        "findings" if locations else "no_findings", 1 if locations else 0,
        args.scope, tool_version=tool_version, count=len(locations), findings=locations,
        coverage="Requested scope under effective Gitleaks rules and exclusions; not proof of absence of secrets.",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", choices=("staged", "files", "history", "pre-push"))
    parser.add_argument("--path", default=".", help="Target repository, directory, or file")
    parser.add_argument("--gitleaks", default="gitleaks", help="Gitleaks executable name/path")
    parser.add_argument("--config", help="Reviewed Gitleaks config; otherwise honor scanner defaults")
    parser.add_argument("--timeout", type=int, default=120, help="Per-command deadline in seconds")
    parser.add_argument("--hook", action="store_true", help="Treat nothing-to-scan as success for staged/pre-push hooks")
    args = parser.parse_args(argv)
    try:
        if args.timeout < 1:
            raise Incomplete("Timeout must be a positive number of seconds.")
        if args.hook and args.scope not in ("staged", "pre-push"):
            raise Incomplete("--hook is supported only for staged and pre-push modes.")
        code = scan(args)
        return 0 if args.hook and code == 3 else code
    except Incomplete as error:
        return emit("incomplete", 2, args.scope, reason=str(error))
    except (OSError, ValueError):
        return emit("incomplete", 2, args.scope, reason="Cannot access the requested path or scanner resources.")


if __name__ == "__main__":
    sys.exit(main())
