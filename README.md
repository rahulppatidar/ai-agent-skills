# AI Agent Skills

Reusable skills for AI coding agents and assistants. Each skill includes agent instructions in `SKILL.md` and a human-facing README.

| Skill | Purpose |
| --- | --- |
| [Token Efficiency](token-efficiency/README.md) | Reduce unnecessary context, tool calls, and output while preserving task quality. |
| [Production Readiness Review](production-readiness-review/README.md) | Assess release risks, operational readiness, verification, and recovery. |

## Installation

With Node.js/npm and Git installed, run this from the project where you want to use the skill:

```bash
npx skills add rahulppatidar/ai-agent-skills --skill token-efficiency --full-depth
```

This uses the third-party [Vercel skills CLI](https://github.com/vercel-labs/skills). Select the agents you use in its prompts. Add `--global` for personal installation across projects.

See [Installation](INSTALLATION.md) for supported agents, manual installation, Windows instructions, activation, and troubleshooting. GitHub installation requires the skill to be pushed to the repository's default branch; local installation is also documented.

## Usage

After installation, ask your agent:

```text
Use the token-efficiency skill for this task.
token-efficiency: balanced

[Your task and relevant files or context]
```

The default mode adapts to task complexity and risk. Review each skill's README for its intended use and limitations. Current version, lifecycle stage, and owner are recorded under `metadata` in its `SKILL.md`.

## Token Savings

No measured savings are published yet. The skill does not install telemetry or automatically count tokens. See [Measuring Token Savings](token-efficiency/MEASUREMENT.md) for usage sources, comparison steps, and honest reporting when counters are unavailable.

## License

See [LICENSE](LICENSE) for the repository's GNU GPL version 3 license text.
