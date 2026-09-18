# find-duplicate-logic

A portable coding-agent skill for finding behaviorally duplicated logic in a repository.

It is designed for agents that support `SKILL.md`-style instructions, and the same instructions can also be adapted into project rules for other coding assistants.

## What it does

It searches for **semantic duplication**, not just copy/paste clones.

Examples:

- two differently named functions implementing the same eligibility rule;
- the same validation duplicated in separate services;
- equivalent calculations expressed with different syntax;
- repeated state transitions or side-effect decisions;
- partial overlap that looks reusable but contains an important policy difference.

It deliberately distinguishes:

- exact duplicate;
- semantic duplicate;
- partial overlap;
- similar but not duplicate.

## When to use

Use this skill before implementing a business rule, reviewing a pull request or working-tree diff, or extracting a shared helper—especially when validation, eligibility, calculations, state transitions, or side-effect logic may already exist under another name.

## Example prompts

For reliable activation, explicitly invoke the installed skill using the syntax in [Client compatibility](#client-compatibility). For example, in Codex:

```text
$find-duplicate-logic Check my current diff for duplicated business logic.
```

The clients can also select it automatically for natural-language requests such as:

```text
Find duplicate logic for calculateRefund().
```

```text
Check my current diff for duplicated business logic.
```

```text
Before implementing prorated subscription refunds, check whether equivalent logic already exists in this repo.
```

```text
Does this validation already exist somewhere under a different name?
```

## Suggested installation

Copy the `find-duplicate-logic` directory into the location your coding agent uses for skills. Keep `SKILL.md` and the `references/` directory together.

After this skill is available on the repository's default branch, install it with the shared installer from the target project's root:

```bash
npx skills add rahulppatidar/ai-agent-skills --skill find-duplicate-logic --full-depth
```

Select Codex, Claude Code, Cursor, or any other supported client in the installer prompts. Add `--global` for a personal installation across projects. To install from this local checkout before publication, run:

```bash
npx skills add ./find-duplicate-logic
```

For tools that do not natively support skills, use the contents of `SKILL.md` as a project command/rule or agent instruction.

See the repository's [installation guide](../INSTALLATION.md) for shared-installer and manual instructions.

## Client compatibility

`SKILL.md` is the portable skill definition. The optional `agents/openai.yaml` file only supplies OpenAI-specific presentation and invocation metadata for ChatGPT and Codex; Claude Code and Cursor use the same `SKILL.md` without requiring equivalent metadata files.

| Client | Project location | Explicit invocation |
| --- | --- | --- |
| Codex | `.agents/skills/find-duplicate-logic/` | `$find-duplicate-logic` |
| Claude Code | `.claude/skills/find-duplicate-logic/` | `/find-duplicate-logic` |
| Cursor | `.agents/skills/find-duplicate-logic/` or `.cursor/skills/find-duplicate-logic/` | `/find-duplicate-logic` or select it with `@` |

All three clients can select the skill automatically from its `description`. Explicit invocation is more reliable when the check is important. These locations and invocation methods were checked against the three vendors' documentation on 2026-09-18; runtime behavior outside Codex has not yet been tested for this skill.

## Limitations

This skill is not intended for byte-for-byte duplicate files or generic copy/paste detection. It can be unnecessary in very small codebases and depends on sufficient domain context to distinguish intentional policy differences.

The skill is diagnostic by default. It does **not** refactor automatically and does **not** assume all duplication should be removed.

## Validation status

Version 1.0 remains at the `review` stage. On 2026-09-18, it passed the local skill-creator structural validator and metadata/UI checks. Target- and diff-mode dry runs correctly distinguished an exact duplicate, a renamed semantic duplicate, and a similar rule with a different domain threshold; the diff run also covered a newly added untracked file. Missing-target and failed-search-scope cases were reported without fabricated findings.

Automatic invocation and runtime behavior across other agent products have not yet been tested.

## Author

Rahul Patidar ([@rahulppatidar](https://github.com/rahulppatidar)).

## License

GNU GPL version 3. See the repository's [LICENSE](../LICENSE).
