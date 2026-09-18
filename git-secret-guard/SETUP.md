# Installation and first run

This guide travels with the skill folder. Install the skill once for your agent, provision its scanner in the execution environment, then enable Git hooks separately in each clone where you want automatic blocking.

## 1. Install the skill for your agent

If you already have this folder, copy the **whole** `git-secret-guard` folder into one location below. Keep `SKILL.md`, `scripts/`, `references/`, `assets/`, and documentation together. Do not overwrite an existing installation without reviewing local customizations.

| Client | Project parent directory | Personal parent directory | Activate and verify |
| --- | --- | --- | --- |
| [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills/` | `~/.claude/skills/` | Start a new session; invoke `/git-secret-guard Check my staged changes for secrets`. |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills/` | `~/.agents/skills/` | Find it in `/skills` or the `$` picker; invoke `$git-secret-guard Check my staged changes for secrets`. |
| [Cursor](https://cursor.com/docs/skills) | `.cursor/skills/` | `~/.cursor/skills/` | Verify under Customize → Skills; type `/` in Agent chat and select `git-secret-guard`. |
| [GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | `.github/skills/` | `~/.copilot/skills/` | Use a skill-capable agent mode/CLI and ask `Use git-secret-guard to check my staged changes for secrets`. Check the client's skill UI/loading evidence when available. |

Each resulting path must end in `git-secret-guard/SKILL.md`. Project paths are relative to your target repository. Personal paths apply across projects for that user; a personal skill does not install hooks in every project. Use one location per client to avoid duplicate copies. Copilot front ends vary; ordinary inline autocomplete is not this workflow.

On Windows, `~` means your user profile directory (usually `C:\Users\your-name`). You can copy the folder in File Explorer or PowerShell. For example, from this repository's root, installing into a separate project's Claude Code folder:

```powershell
$skillParent = 'C:\work\my-project\.claude\skills'
$skillDestination = Join-Path $skillParent 'git-secret-guard'
if (Test-Path $skillDestination) { throw 'Skill already exists; review before updating.' }
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
Copy-Item -Recurse .\git-secret-guard -Destination $skillDestination
```

For macOS/Linux, from this repository's root, the corresponding example is:

```bash
mkdir -p /path/to/my-project/.claude/skills
cp -R -i git-secret-guard /path/to/my-project/.claude/skills/
```

Substitute the directory from the table for your client. With WSL, SSH, containers, or cloud agents, copy/install into the filesystem actually running the agent; a host-machine install is not automatically present there. Cloud skill availability and command permissions depend on the client. Use current clients with Agent Skills support; these paths do not certify runtime compatibility with every version.

### Optional shared installer

With Node.js/npm and Git available, the third-party [Vercel skills CLI](https://github.com/vercel-labs/skills) can copy skills for your chosen clients. From the target project, point it at this local checkout:

```bash
npx skills add /absolute/path/to/ai-agent-skills/git-secret-guard
```

On Windows replace the source with a quoted Windows path. Select your client in the prompts; `--global` selects personal installation. Until the skill is published on the remote default branch, use that local source. After publication:

```bash
npx skills add rahulppatidar/ai-agent-skills --skill git-secret-guard --full-depth
```

Node.js is needed only for this installer, not for the scanner or hooks. The complete shared client catalog is also [available online](https://github.com/rahulppatidar/ai-agent-skills/blob/main/INSTALLATION.md); this guide does not depend on a parent file surviving installation.

## 2. Check and install prerequisites

The skill includes a two-phase bootstrap. First it performs a read-only platform/tool check and prints an exact installation plan. The agent explains the plan and asks once. Only after you approve that plan ID does it install and verify the missing mandatory tools.

| Workflow | Mandatory tools | Not required |
| --- | --- | --- |
| `scan` | Gitleaks | Git for a plain folder scan; Python |
| `pre-commit` | Git, Gitleaks | Python; `pre-commit` framework |
| `pre-push` | Git, Gitleaks, Python 3.9+ | Node.js; Python packages; cloud account |

From the installed skill directory, the read-only check is:

```bash
# macOS, Linux, or WSL
sh scripts/setup.sh check pre-push
```

```powershell
# Windows PowerShell
& .\scripts\setup.ps1 -Action Check -Workflow pre-push
```

Replace `pre-push` with `scan` or `pre-commit` to avoid installing tools that workflow does not need. Status `ready` means nothing will be installed. Status `confirmation-required` and exit code 10 are intentional: the output includes missing tools, sources, destinations, package commands, network/elevation needs, and a `plan-id`. The agent must summarize why each item is needed and ask for your approval of that exact plan.

After you confirm, the agent runs the corresponding command with the returned ID:

```bash
sh scripts/setup.sh install pre-push --approve PLAN_ID
```

```powershell
& .\scripts\setup.ps1 -Action Install -Workflow pre-push -Approve PLAN_ID
```

Install mode recalculates the plan and refuses a missing, wrong, or stale ID. It uses Homebrew when already present on macOS; a recognized system package manager on Linux; or winget when already present on Windows for missing Git/Python. It downloads Gitleaks 8.30.1 only from its official GitHub release, verifies the published SHA-256, and installs it to `~/.local/bin` (macOS/Linux) or `%LOCALAPPDATA%\GitSecretGuard\bin` (Windows). It does not automatically install a package manager or modify PATH. The verified absolute paths in its final output are used by repository-local hook configuration.

You may still see the operating system's own `sudo`, UAC, package-license, or reboot/restart prompt; the skill cannot safely bypass those controls. If the detected manager is unsupported, the bootstrap stops and the agent offers the manual route below. Run setup separately inside WSL, a container, SSH host, or cloud agent when that environment executes the hooks. Hooks themselves never install software or prompt; missing tools make them fail closed.

Python is needed only by the bundled redacted report/pre-push helper. No Python packages are installed. The helper accepts Gitleaks 8.19+ in the 8.x series; **8.30.1 is tested here**. Offline scanning needs no cloud account or API key.

### Manual fallback

If automatic setup is unavailable or you prefer manual control, install Git from [git-scm.com](https://git-scm.com/downloads) and Python from [python.org](https://www.python.org/downloads/) or the operating system's supported package manager. Windows native shell hooks need Git for Windows' shell. Verify `git --version`, `gitleaks version`, and `python3 --version` (`py -3 --version` on Windows).

#### Gitleaks on macOS

With Homebrew already installed, the [official Gitleaks guide](https://github.com/gitleaks/gitleaks#installing) supports:

```bash
brew install gitleaks
gitleaks version
```

Homebrew selects its current formula version. For reproducible team/CI setup, use the reviewed release binary below and record the version instead of assuming the formula is pinned.

#### Pinned binaries on Linux, Windows, or macOS

Open the official [Gitleaks 8.30.1 release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1). Download the matching archive plus `gitleaks_8.30.1_checksums.txt`. Choose `linux_x64`/`linux_arm64`, `windows_x64`/`windows_arm64`, or `darwin_x64`/`darwin_arm64` for your actual OS and CPU. Use a later reviewed security release if your organization requires it, updating the version and checksum together.

Before extracting, calculate the archive's SHA-256 and compare the full digest with its exact filename in the downloaded checksums file:

```bash
# Linux example, in the download directory
sha256sum gitleaks_8.30.1_linux_x64.tar.gz
# macOS example
shasum -a 256 gitleaks_8.30.1_darwin_arm64.tar.gz
```

```powershell
# Windows PowerShell example
Get-FileHash .\gitleaks_8.30.1_windows_x64.zip -Algorithm SHA256
```

Do not execute the binary if the digest differs. Extract into a dedicated user-owned directory. PATH changes are optional: `scan.py` accepts `--gitleaks`, and the bundled hooks read absolute paths from repository-local Git configuration.

Verify with `gitleaks version` and `gitleaks git --help`. `command -v gitleaks` (macOS/Linux) or `Get-Command gitleaks` (PowerShell) shows which binary will run. Install into WSL/container/remote environments separately when they run the commands. Downloads/installers require network access; the configured local scanner does not need to verify credentials online.

## 3. Run a first check

In your target repository, ask the agent:

```text
Use git-secret-guard to check my staged changes for secrets.
Check prerequisites first and report locations without revealing credential values.
```

The expected result names the scanner/version and scanned scope, then reports findings, no findings in that scope, an incomplete scan, or nothing staged. If nothing is staged, it should not claim the entire repository is clean. To scan a folder instead, ask `Use git-secret-guard to scan this folder's current files for exposed credentials` and supply its path.

For a manual run, set the absolute paths below to your installed helper and target repository:

```bash
python3 /absolute/path/to/git-secret-guard/scripts/scan.py staged --path /path/to/project
```

```powershell
py -3 'C:\path\to\git-secret-guard\scripts\scan.py' staged --path 'C:\work\my-project'
```

Successful scans emit JSON with `status: "no_findings"`, `scope: "staged"`, and `count: 0`; findings include only file/line/rule/commit metadata. Exit codes are 0 for no findings, 1 for findings, 2 for incomplete/error, and 3 for nothing to scan. Files/history modes are described in the [scanner guide](references/scanners.md). Do not test with a real key.

## 4. Enable automatic protection

Ask:

```text
Use git-secret-guard to set up pre-commit and pre-push protection here.
Preserve existing hooks, document contributor setup, and demonstrate blocking
in a temporary repository using synthetic credentials.
```

Follow [Protection setup](references/protection.md) for integration, including bundled native pre-commit and pre-push templates. The agent records the verified absolute Python/Gitleaks paths in local Git configuration, so you do not need to edit PATH. Pre-push requires a project-local copy of `scan.py`; the agent should document where it placed those files and how contributors enable the hook. The helper scans full ancestry of outgoing tips, so old leaks already on the remote may also block; it is not an incremental new-secrets-only gate.

Only projects choosing the `pre-commit` framework need that additional package. Follow its [installation guide](https://pre-commit.com/#install), verify `pre-commit --version`, then run `pre-commit install` in each clone after merging the configuration. A native hook does not require the framework. Do not install a framework-managed pre-push hook over the bundled native one: it must preserve or replay Git's ref-update stdin.

Every contributor needs the scanner/runtime and hook activation in their own clone. Commit the shared config/helper and contributor instructions; local `.git/hooks` files do not propagate simply by pushing a branch. Verify both a clean operation and a synthetic blocked operation in disposable repositories. Hosted CI/branch rules/push protection need separate configuration and permissions; local success does not prove remote enforcement.

## Troubleshooting

| Symptom | Check or action |
| --- | --- |
| Skill is not discovered | Correct client directory, exact `git-secret-guard/SKILL.md` nesting, current client, workspace trust, and a new session. Confirm visible loading, not just an assistant's claim. |
| `gitleaks`/Python not found | Rerun the bootstrap check in the hook's environment. Verify `secretguard.gitleaksPath` and `secretguard.pythonPath` in the target clone; restart after an OS installer when requested. |
| Plan ID is refused | The environment changed after approval or the ID was copied incorrectly. Run check again, review the new plan, and confirm it; never bypass the binding. |
| Unsupported scanner/unknown flags | Check `gitleaks version` and `gitleaks git --help`; install the reviewed binary after confirming the plan. The helper fails rather than switching to an unverified interface. |
| Scan says incomplete | Address its named prerequisite, invalid config, conflicts, missing history, or timeout. Do not treat it as a passed security check. |
| No staged changes | Stage only the intended files, or choose a files/history audit. The skill does not stage everything automatically. |
| Hook never runs | Check `git config --show-origin --get core.hooksPath` and `git rev-parse --git-path hooks`; verify the correct hook is executable, with LF line endings and available tools. A config file alone is insufficient. |
| Push scan gets no updates | Native Git supplies stdin; terminal invocations or a hook manager that consumes stdin are not a valid proof of coverage. Test via a real push to an isolated local bare repository. |
| Old secret blocks a new push | Full outgoing ancestry is deliberately scanned. Rotate exposed credentials and review cleanup/exception policy; don't bypass or baseline a live secret. |
| False positive | Ask the agent to explain it and add only a narrow justified exception; never exempt whole documentation/test directories by default. |

Vendor documentation checked 2026-09-18. Linux bootstrap checks, scanner, and native-hook execution are tested without performing live system installation; Windows/macOS installers and hosted enforcement are documentation-reviewed only. See [validation evidence](VALIDATION.md) for exact coverage.
