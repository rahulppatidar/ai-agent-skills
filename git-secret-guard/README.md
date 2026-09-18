# Git Secret Guard

Catch exposed credentials before a commit, add repeatable protection, or work through an accidental leak. Applies to source code, configuration, documentation, and other text regardless of language or framework. The bootstrap detects the platform and missing mandatory tools, then asks once before installing an exact, reviewable plan.

## Use it

Start with the bundled [installation and first-run guide](SETUP.md). It covers Claude Code, Codex, Cursor, and GitHub Copilot; Windows/macOS/Linux prerequisites; activation; and troubleshooting. Then ask:

```text
Use git-secret-guard to check what I am about to commit for secrets.
```

Other useful requests:

- “Set up secret protection in this repository. Preserve our existing hooks.”
- “Enable pre-commit and pre-push protection, and document how teammates activate it.”
- “Audit this folder and Git history before I make the project public.”
- “I committed an API key. Help me fix it without losing unrelated work.”
- “Review this scanner finding and add an exception only if it is a false positive.”

You get a result, the scope actually scanned, redacted finding locations, and specific next steps. The skill distinguishes an incomplete scan from a scan with no findings. It accounts for partial staging, first commits, secrets deleted from history's latest snapshot, and existing scanner policy.

## Tools and protection

Uses a suitable scanner already configured in the project, or defaults to [Gitleaks](https://github.com/gitleaks/gitleaks). Includes guidance for detect-secrets, TruffleHog, and other existing integrations. It does not install every scanner or upload code to a scanning service automatically.

For missing dependencies, the agent runs the bundled read-only check, explains what is needed, and shows one plan with a unique ID, source, destination, commands, and privilege/network needs. After you approve that exact plan, the bootstrap installs and verifies only the missing mandatory tools. A changed plan needs new approval. You can decline; the agent then uses a compatible existing workflow or reports what is blocked. It does not install a hook manager, Homebrew, winget, or unrelated language tooling.

The [scan helper](scripts/scan.py) requires Python 3.9+ and Gitleaks 8.19+ in the 8.x series; 8.30.1 is tested. Git is needed for repository modes. It emits JSON containing finding metadata instead of secret values or source snippets. The bundled pre-push workflow uses this helper; native pre-commit scanning can use Gitleaks directly without Python. Run `python3 scripts/scan.py --help` from this skill folder for usage. The helper's output can still contain private filenames; review metadata before sharing.

An installed skill is advice and workflow, not an always-running Git hook. A setup request installs or configures actual protection within your authorized scope. Hooks catch problems locally, required CI checks can block merges after upload, and server push protection can reject supported secrets before remote acceptance. Contributor setup and hosting permissions still matter.

## Limitations and evidence

No scanner detects every secret. This skill does not establish that a repository contains no PII, confidential business data, image-embedded secrets, encrypted content, or unfetched objects. Network verification is optional and must be authorized. A finding is not proof a credential is active; an unverified finding is not proof it is harmless.

Version 1.2 is at **review** stage. Pre-push scans full reachable history of outgoing commit tips, including merge changes; older leaks can block, even if already on the remote. It does not inspect commit/tag messages or support tags pointing directly to non-commit objects. See [validation evidence and remaining gaps](VALIDATION.md). Agent Skills instructions are portable to compatible clients with local tools; `agents/openai.yaml` is OpenAI-specific. Cross-client execution and automatic discovery are not established merely by the file format.

Authored by Rahul Patidar. Licensed GPL-3.0-only; [the bundled license](LICENSE) also covers standalone distribution. External scanners retain their own licenses.
