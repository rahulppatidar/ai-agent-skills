# Scanner guide

Use this reference when running a scan or selecting a backend. Commands below use Gitleaks' modern `git`, `dir`, and `stdin` interface; `detect`/`protect` are deprecated. Confirm installed flags with `--help`. The tested version is recorded in [validation](../VALIDATION.md).

## Default: Gitleaks with a metadata-only report

The bundled `scripts/scan.py` requires Python 3.9+, Git for Git modes, and Gitleaks 8.19+ (8.x). It performs local detection only. Use the two-phase bootstrap in [Setup](../SETUP.md) to detect and, after one exact-plan confirmation, install missing mandatory tools. Gitleaks need not be on PATH when passed with `--gitleaks`. Resolve the script relative to the installed skill directory, not the repository being scanned:

```bash
python3 /path/to/git-secret-guard/scripts/scan.py staged --path /path/to/repository
python3 /path/to/git-secret-guard/scripts/scan.py files --path /path/to/folder
python3 /path/to/git-secret-guard/scripts/scan.py history --path /path/to/repository
```

On Windows use the verified Python executable emitted by the bootstrap. `--gitleaks` accepts a scanner executable path, `--config` selects an existing reviewed Gitleaks config, and `--timeout` sets the per-command deadline in seconds (default 120). The scanner command itself never installs dependencies; only the separately confirmed bootstrap install phase may do so.

Exit codes: **0** = no findings in the requested scope; **1** = findings; **2** = incomplete/error; **3** = nothing to scan. The JSON report contains scope, tool version, count, and `file`, `line`, `rule`, `commit` fields. It never forwards raw scanner stdout/stderr or finding snippets. Report metadata can still reveal confidential paths; do not publish it without reviewing it.

`pre-push` mode is for native Git hook stdin, not a normal terminal audit; follow [Protection setup](protection.md). It scans the full ancestry of outgoing commit tips, including merge diffs, and supports tags resolving to commits. Use `--hook` only for staged/pre-push hooks: nothing-to-scan then exits 0 while its JSON status remains explicit. Findings and errors still block. A bare invocation with empty stdin does not test push protection.

The helper rejects shallow history, unresolved index conflicts, and a changed index during a staged scan. Staged mode scans added diff lines from the index, not every unchanged line in staged file snapshots; use files/history modes for an audit of existing secrets. File scans support directories and individual files outside Git. History means reachable commits across available local refs, not unreachable objects or all remote history. Empty folders and scanner exclusions can still yield zero findings; the helper is not a file-format coverage attestation. Review `.gitleaks.toml`, `.gitleaksignore`, inline allowances and `GITLEAKS_CONFIG`/`GITLEAKS_CONFIG_TOML` selection separately. It honors existing scanner policy and does not automatically baseline or suppress findings.

Equivalent scanner commands for a hook/CI integration are:

```bash
gitleaks git --pre-commit --staged --redact=100 --no-banner .
gitleaks dir --redact=100 --no-banner /path/to/folder
gitleaks git --log-opts="--all --full-history -m" --redact=100 --no-banner .
```

Use the helper for agent-facing reports when practical. `--redact` is essential but does not make arbitrary diagnostics, source context, or other report fields safe to publish. Do not add `--verbose`, dump raw JSON, or retain report artifacts by default. Native scanner exit codes differ from the helper's contract; any nonzero scan exit blocks the hook or CI check.

For custom Gitleaks rules, extend built-in detection with `[extend]` and `useDefault = true` unless replacement is intentional. Prove custom patterns with positive and negative synthetic cases. Avoid generic entropy-only rules that make every lockfile block a commit.

## When another tool fits better

| Tool | Prefer it when | Required care |
| --- | --- | --- |
| [detect-secrets](https://github.com/Yelp/detect-secrets) | The project already uses its plugins and audited baseline | A new baseline can conceal existing credentials. Review findings first; disable network verification for offline use. A staged filename list alone scans working files; use the hook framework's staged handling and test partial staging. |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | The user needs an independent scan, broader source coverage, or authorized credential verification | Set `--no-verification` for offline detection and check update/network behavior for the installed version. Do not use a verified-only filter for an offline gate. Raw JSON includes secret fields; filter in-process before exposing output. |
| [ggshield](https://docs.gitguardian.com/ggshield-docs/home) | The organization already uses GitGuardian | Standard service-backed scanning sends content to the configured API; confirm authorization and account requirements. Keep secrets hidden. |
| [Trivy](https://trivy.dev/docs/latest/scanner/secret/) | Existing Trivy infrastructure also needs files/image secret scanning | Repository/filesystem scans are not evidence that every Git commit was scanned. Limit scanners to the requested task. |
| [git-secrets](https://github.com/awslabs/git-secrets), [Talisman](https://github.com/thoughtworks/talisman) | Existing hooks or organization-specific rules already depend on them | Verify actual rule coverage, update/network behavior, and staged-content handling before relying on the gate. |

Use official releases or the project's trusted package manager; pin reviewed versions and verify published checksums/signatures when downloading binaries. Follow the dependency confirmation flow in `SKILL.md` before downloads, installs, upgrades, or PATH changes; explain the purpose, location, and required access first. Do not pipe an installation script from the network into a shell. Keep tool installation scoped to the approved plan and environment permissions. Reuse existing hooks, baselines, and policies where valid; avoid stacking redundant scanners on every commit.

References checked 2026-09-18: [Gitleaks usage](https://github.com/gitleaks/gitleaks), [official hook definitions](https://github.com/gitleaks/gitleaks/blob/master/.pre-commit-hooks.yaml). Alternative backend integrations are guidance, not bundled/tested adapters.
