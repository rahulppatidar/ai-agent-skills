# Validation evidence

## Status: review, 2026-09-18

Version 1.2 was evaluated in a Codex session identified as GPT-6, with independent Codex/GPT-6 subagent passes for scanning and earlier pre-push/setup changes. The exact hosted model build is not exposed. This is not a cross-client certification or a measured comparison against an agent without the skill.

Environment: Linux x86_64, Python 3.10.12, Git 2.34.1, Gitleaks 8.30.1. The scanner was downloaded from its official release into a temporary directory and its SHA-256 matched the release API's published digest. No scanner or skill was installed globally, and no real credential was used. All Git commits and hook exercises occurred in disposable fixture repositories.

## Repeatable tests

From the repository root, with an installed Gitleaks executable:

```bash
GITLEAKS_TEST_BINARY=/absolute/path/to/gitleaks python3 -B -m unittest discover -s git-secret-guard/tests -v
```

For a standalone skill folder use `-s tests` instead. On PowerShell set `$env:GITLEAKS_TEST_BINARY` and use `py -3 -B -m unittest discover -s tests -v`. Without a Gitleaks executable, integration tests are skipped; that does not establish scanner behavior.

**52 tests passed:** 33 real-scanner/hook integration tests, 12 report/failure-contract tests, and 7 bootstrap planner tests. Tests cover:

- Clean and secret-bearing first commits, using a synthetic built-in `github-pat` detector fixture.
- A secret remaining staged after the working file is cleaned, and the inverse: clean staged content with an unstaged secret.
- Preservation of the index and working tree during scans.
- Empty index/history, a non-Git directory, individual hidden files, spaces/Unicode in paths, and missing targets.
- Secrets deleted in later commits and secrets on a noncurrent branch.
- Shallow-history rejection, conflicted index rejection, and simulated index changes during scanning.
- Real malformed scanner configuration; mocked missing executable, timeouts, malformed reports, error diagnostics, and exit/report disagreements.
- Explicit output-field selection, excluding secret/snippet/author/description fields from displayed JSON and withholding raw error output.
- Custom rules extending built-in detection.
- A real native POSIX Git hook blocking a synthetic staged credential, preserving an existing hook step, and accepting a corrected first commit.
- Native hook failures when the scanner is absent or its configuration is invalid.
- Real local bare-remote pushes: clean initial/update/tag/deletion operations; blocked historical leaks, noncurrent refs in multi-ref pushes, annotated/lightweight commit tags, and merge-resolution leaks. Failed pushes leave remote refs unchanged.
- Clean and unsafe force pushes, ignoring unrelated local branches, missing remote-base objects, malformed protocol input, unsupported blob tags, shallow-history refusal, missing scanners, and invalid configuration.
- Hook-only mapping of nothing-to-scan to success without masking findings/errors or changing audit exit codes.
- Read-only Linux prerequisite detection, user-local Gitleaks discovery without PATH edits (including precedence over an outdated PATH version), supported-version checks, smallest-workflow dependency selection, stable plan IDs, and refusal of missing/wrong approval IDs before any installation.
- Bundled pre-commit and pre-push templates resolving verified absolute executables from repository-local Git configuration.

## Independent behavior and discovery review

The independent evaluator read the skill and executed its helper in a separate disposable fixture. It confirmed detection in the index despite a sanitized working file, a clean result after restaging, byte-for-byte preservation of the index/working file, an incomplete result for a missing scanner, and “nothing to scan” for an empty index. Both the command sequence and result assertions were inspected. An initial sequential-alphabet fixture was not detected; a deterministic randomized synthetic token exercised the actual built-in detector. This is a reminder that credential shape alone is not a coverage guarantee.

Missing-path and pushed-production-key scenarios were assessed against the instructions: request an identifiable target when none exists; prioritize rotation guidance while preserving provider permissions and requiring specific authorization for shared-history rewrites. These were scenario reviews, not live provider incident exercises.

A second independent native-hook run exercised nine workflow cases, including real local pushes, multi-ref blocking, a non-HEAD branch with a secret added then deleted, commit tags, unrelated branches, deletion, and a fresh contributor clone. The clone received the shared helper/template but required explicit local hook activation before protection applied. Missing-scanner pushes failed without changing remote refs. The execution script and assertions were reviewed. Two documentation corrections followed: the scanner-help command and the risk of writing to a shared `core.hooksPath` directory.

Dependency setup was first assessed through missing-Python/scanner and declined-confirmation scenarios. Version 1.2 adds standalone macOS/Linux/WSL shell and Windows PowerShell bootstraps: read-only check emits a reviewable plan ID, install mode recalculates that plan and refuses missing/wrong/stale approval, official Gitleaks downloads are checksum-verified, and hooks consume emitted absolute paths. The Linux check/consent paths were executed in temporary homes with fake tool versions; no network, package-manager installation, OS configuration, or live install path was exercised.

Description-only manual routing assessment:

| Prompt | Expected selection |
| --- | --- |
| Check what I am about to commit for secrets. | Yes: staged scan |
| Add a hook that prevents API keys entering Git. | Yes: protection setup |
| I pushed a production credential; help clean it up. | Yes: leak response |
| Review this release for production readiness. | No automatic selection solely from this prompt |
| Find customer PII in exported CSVs. | No: separate privacy workflow |
| Deploy a secrets manager and configure application access. | No automatic selection solely from this prompt |

This assesses the description separately from explicit invocation; actual client auto-discovery was not tested.

## Structural checks and remaining gaps

The bundled skill-creator validator, separate metadata/UI assertions, local Markdown link checks, Python and POSIX shell syntax checks, and whitespace checks passed. The new skill folder was also scanned with the helper/Gitleaks with no findings. The Agent Skills specification and relevant instruction-design guidance were consulted; official Claude Code, Codex, Cursor, and Copilot documentation informed the standalone setup guide. The standalone `skills-ref` validator was not run.

Not exercised: macOS/Windows bootstrap runtime behavior (PowerShell was reviewed only), successful bootstrap downloads/system-package installs, actual client installations/discovery, the `pre-commit` framework itself, existing multi-consumer pre-push dispatchers, hosted CI/branch rules/push protection, older supported Gitleaks versions, alternative scanner integrations, provider verification or rotation, real-history cleanup, and large/binary/archive/LFS/submodule coverage. The push helper scans reachable file changes, not commit/tag messages. No efficiency or detection-rate benchmark was performed. These gaps keep the lifecycle at review.
