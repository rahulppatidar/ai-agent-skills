# Protection setup

Read when the user asks to install or improve prevention. Establish the repository, existing hook manager, CI provider, and enforcement boundary from available files. Reuse working protections. Creating a skill does not itself install hooks into the target repository.

## 1. Protect the local commit

Integrate Gitleaks into the current hook manager. Preserve existing commands and failure propagation. Avoid changing global Git configuration or replacing `core.hooksPath`; inspect its origin and the effective hook directory first. An absolute or globally configured hook directory may serve other repositories. Do not write there under a single-repository setup request: explain the scope and obtain explicit authorization for shared changes, or agree on a repository-local integration that preserves existing shared checks.

For a project using [pre-commit](https://pre-commit.com/#repository-local-hooks), merge this local entry into its existing configuration. It assumes a pinned Gitleaks binary is provisioned for each developer and CI worker:

```yaml
repos:
  - repo: local
    hooks:
      - id: git-secret-guard
        name: Guard staged changes against secrets
        entry: gitleaks git --pre-commit --staged --redact=100 --no-banner
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
```

`pass_filenames: false` makes the scanner inspect the actual index. Even `pre-commit run --all-files` with this entry still scans staged changes; use the separate files/history commands for an audit. Do not add file-extension filters: credentials also occur in documentation, extensionless files, and generated artifacts. Configure installation for contributors (`pre-commit install`) and explain that committing a YAML file alone does not install a hook in every clone. If no hook framework exists, a repository-local native hook is sufficient; do not introduce a Node/Python project dependency merely because that is the agent's familiar stack.

For a native hook, use the bundled [pre-commit template](../assets/pre-commit). After the bootstrap verifies Gitleaks, record the emitted absolute path in this clone:

```bash
git config --local secretguard.gitleaksPath /absolute/path/to/gitleaks
```

The local setting is untracked and must be set in each clone. Install the template into the effective hook directory only after inspecting and preserving any existing hook. For an existing shell hook, the equivalent scanning step is:

```sh
gitleaks git --pre-commit --staged --redact=100 --no-banner . || exit "$?"
```

A missing executable also fails this command. Preserve earlier and later hooks; use `exec` only if this is intentionally the last command. Provisioning instructions must explain how to install the pinned scanner. The bundled Python scan helper is optional and need not become a permanent dependency of the protected project.

## 2. Protect local pushes

The bundled [native pre-push template](../assets/pre-push) runs [scan.py](../scripts/scan.py) in `pre-push --hook` mode. Git supplies one ref-update record per pushed ref on stdin. The helper validates the object IDs, peels commit tags, and scans full reachable file-change history of all outgoing commit tips, including merge diffs. It handles new branches, multiple refs, and force pushes without depending on local copies of remote base commits. Ref deletions and empty updates have nothing to scan. Unsupported blob/tree tags, missing objects, shallow history, malformed input, and scanner errors block.

This conservative gate can flag old leaks already present on the remote. It avoids scanning unrelated local branches, but is not an incremental range scanner. Explain the tradeoff before enabling it in large/legacy repositories; use an existing well-tested incremental gate if one already exists. Do not bypass failed checks to make it faster.

For a repository with no existing pre-push hook:

1. Provision Python 3.9+ and Gitleaks with the `pre-push` bootstrap described in [Setup](../SETUP.md). Capture the verified `python-path` and `gitleaks-path` output.
2. Copy `scripts/scan.py` to `.secret-guard/scan.py` in the target repository and the bundled `LICENSE` to `.secret-guard/LICENSE`. Keep the source attribution. Review existing destination files before merging or updating them; do not overwrite silently. This project-local copy makes the hook independent of a contributor's personal skill installation. Distribute it in accordance with its GPL-3.0-only license.
3. Store those absolute paths in repository-local Git configuration: `git config --local secretguard.pythonPath /absolute/path/to/python` and `git config --local secretguard.gitleaksPath /absolute/path/to/gitleaks`. Quote paths containing spaces. These untracked per-clone values avoid PATH edits and work with Git for Windows' shell.
4. From the target root, inspect `git config --show-origin --get core.hooksPath` (no output/unset is normal) and `git rev-parse --git-path hooks`. Copy `assets/pre-push` to `pre-push` in that effective hook directory only if no hook exists. Use LF line endings and make the file executable on POSIX systems. For the default directory: `chmod +x .git/hooks/pre-push`. Use the resolved path instead when customized.
5. Commit the reviewed helper/license and a tracked copy of the hook template or setup instructions. Each contributor runs the bootstrap and activates/configures the local hook after cloning; Git does not distribute `.git/hooks` or local Git config with ordinary commits. Test with real pushes to an isolated local bare remote.

If a pre-push hook or manager already exists, integrate rather than replacing it. Git's stdin must reach every consumer. Do not append this helper after a command that drained stdin; use the manager's documented replay mechanism or a reviewed dispatcher. In particular, do not add `scan.py pre-push` as an ordinary `pre-commit` framework entry that receives no ref-update stdin. Preserve all existing checks and their nonzero statuses. The standalone template's `exec` is only appropriate when it is the final/sole hook command.

`--hook` maps “nothing to scan” to exit 0 for Git while retaining that JSON status. Findings/errors stay nonzero. Normal audit commands keep exit 3 for nothing to scan. The helper never pushes, fetches, changes refs, or calls credential providers; Git performs the requested push only after the hook passes.

## 3. Protect review and server boundaries

Configure a required CI check when it is in the requested scope. Local hooks can be bypassed; a CI check blocks merging only when branch rules require it, and it runs after the source has reached the remote. Do not call CI a guarantee against uploading secrets.

Use the same reviewed scanner rules and a pinned binary/container/action. Restrict workflow permissions and avoid privileged execution of untrusted PR code. Scanner config, workflow, baseline, and allowlist changes should themselves require review. Do not use `continue-on-error`, `|| true`, an always-zero scanner option, or an unrestricted bypass.

For small repositories, fetch the intended complete history and run:

```bash
gitleaks git --log-opts="--all --full-history -m" --redact=100 --no-banner .
```

For larger repositories, use an explicit verified base/head commit range that includes every incoming commit; document that it is incremental. Fetch missing commits within scope before claiming coverage. Handle first pushes, new branches, force pushes, merges, and PRs from forks; an empty or invalid base must fail or trigger a broader scan, not silently pass. Never limit protection to the final PR diff: an intermediate commit may contain a secret later removed.

Where supported, add server-side push protection or a pre-receive gate to reject secrets **before the remote accepts them**. [GitHub push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection) has supported-pattern and bypass limits; [GitLab secret push protection](https://docs.gitlab.com/user/application_security/secret_detection/secret_push_protection/) also depends on host capabilities and configuration. Respect the user's existing authority for remote settings; report a concrete pending setting if you cannot apply it. Do not claim remote enforcement from a workflow file alone.

## 4. Demonstrate the protection

Test in an isolated disposable repository using synthetic values, never a real credential. If the host skips commits during testing, invoke the installed hook directly and state that limitation. Confirm:

- A clean staged change passes, including the first commit.
- A synthetic detector-matching credential blocks and never appears unredacted in displayed output.
- A staged credential still blocks after its working file has been cleaned without restaging.
- A clean staged file is not blocked solely by an unrelated unstaged fixture.
- An unavailable scanner and invalid configuration fail instead of silently passing.
- A history scan finds a synthetic secret introduced then deleted in earlier commits.
- Existing hooks still run and the original repository/index remain intact.
- A pre-push hook blocks a secret added then deleted before the outgoing tip, and a secret introduced by a merge resolution.
- Clean first pushes/updates/deletions succeed; multi-ref/tag/force pushes are checked using Git's actual input and failed pushes leave remote refs unchanged.

If tests use a dedicated custom detector, also test a synthetic value matching a built-in detector. A custom-rule-only test does not establish built-in coverage. Pin any test suppression to synthetic test data only.

Finish with the installed/configured/enforced distinction, test evidence, and contributor setup instructions. Do not promise 100% detection or silently disable a gate to unblock a commit. Documentation checked 2026-09-18; live hosting enforcement must be verified in the actual target account.
