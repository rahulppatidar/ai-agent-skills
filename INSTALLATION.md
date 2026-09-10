# Installing Skills

These instructions apply to `token-efficiency` and `production-readiness-review`. Examples use `token-efficiency`; substitute the other directory name to install that skill.

Documentation checked on 2026-09-10. Paths below are documented by the linked vendors; installation has not been tested inside every listed client. Use a current client version with Agent Skills support. The agent or extension determines support, not the IDE alone.

## Shared Installer

Prerequisites: Node.js/npm (providing `npx`), Git, and your chosen agent. Run from your target project's root:

```bash
npx skills add rahulppatidar/ai-agent-skills --skill token-efficiency --full-depth
```

Select your agents in the prompts. `--full-depth` includes this repository's top-level skill folders. Optional flags:

| Flag | Use |
| --- | --- |
| `--global` | Personal installation across projects. |
| `--agent codex --agent claude-code` | Target selected agents. |
| `--copy` | Copy instead of using symlinks. |
| `--list` | Inspect available skills without installing. |

The third-party [Vercel skills CLI](https://github.com/vercel-labs/skills) documents additional agents and update/removal commands. Its installation paths may use compatible shared directories instead of the vendor-specific paths below. Do not install duplicate copies through both methods.

Repository-name installs read the remote default branch. Until these files are merged there, clone the branch containing them and install locally:

```bash
npx skills add ./ai-agent-skills/token-efficiency
```

## Manual Installation

Clone the repository outside the target project, or download its ZIP from GitHub and extract it:

```bash
git clone https://github.com/rahulppatidar/ai-agent-skills.git
```

Copy the complete `token-efficiency` directory into one chosen parent directory below. The resulting path must end in `token-efficiency/SKILL.md`, with exactly that capitalization. Project paths are relative to the target project; `~` means your home directory.

| Agent or IDE integration | Project parent directory | Personal parent directory | Vendor documentation |
| --- | --- | --- | --- |
| Codex CLI / local IDE integration | `.agents/skills/` | `~/.agents/skills/` | [Codex](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code CLI / IDE integration | `.claude/skills/` | `~/.claude/skills/` | [Claude Code](https://code.claude.com/docs/en/skills) |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` | [Cursor](https://cursor.com/docs/skills) |
| GitHub Copilot agent mode in VS Code / JetBrains, or CLI | `.github/skills/` | `~/.copilot/skills/` | [GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` | [Gemini CLI](https://geminicli.com/docs/cli/skills/) |
| Windsurf / Cascade | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` | [Cascade](https://docs.windsurf.com/windsurf/cascade/skills) |
| Cline | `.cline/skills/` | `~/.cline/skills/` | [Cline](https://docs.cline.bot/customization/skills) |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` | [OpenCode](https://opencode.ai/docs/skills) |
| Google Antigravity | `.agents/skills/` | `~/.gemini/antigravity/skills/` | [Antigravity](https://www.antigravity.google/docs/ide/skills/) |
| JetBrains Junie | `.junie/skills/` | `~/.junie/skills/` | [Junie](https://junie.jetbrains.com/docs/agent-skills.html) |

For example, install for Claude Code on macOS/Linux, starting in the directory containing the clone:

```bash
mkdir -p ~/.claude/skills
cp -R -i ./ai-agent-skills/token-efficiency ~/.claude/skills/
```

On Windows PowerShell, with the clone in the current directory:

```powershell
$skillParent = Join-Path $env:USERPROFILE '.claude\skills'
$skillDestination = Join-Path $skillParent 'token-efficiency'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
if (Test-Path $skillDestination) {
    throw 'token-efficiency already exists. Review the installed copy before updating.'
}
Copy-Item -Recurse -Path .\ai-agent-skills\token-efficiency -Destination $skillDestination
```

Use the appropriate parent directory from the table for other agents. For a project installation, use the target project's path instead of your home directory. When the agent runs in WSL, a container, SSH, or a remote workspace, install into that environment's filesystem.

## Native Installation Options

In Codex, the built-in installer can download from a repository:

```text
$skill-installer Install token-efficiency from
https://github.com/rahulppatidar/ai-agent-skills
using the token-efficiency directory.
```

See [Codex skill installation](https://learn.chatgpt.com/docs/build-skills). For installable distribution through the OpenAI plugin directory, a separate plugin package is required; this repository currently distributes skill folders.

Gemini CLI also supports a repository subdirectory and installation scope:

```bash
gemini skills install https://github.com/rahulppatidar/ai-agent-skills.git --path token-efficiency --scope user
```

Use `--scope workspace` for a project installation. See [Gemini skill management](https://geminicli.com/docs/cli/skills/).

## Activate and Verify

Start a new agent conversation after installation. Confirm `token-efficiency` appears in its skill list or picker, then explicitly invoke it for the first task:

| Client | Activation or discovery |
| --- | --- |
| Codex | Use `$token-efficiency` with your task. |
| Claude Code | Use `/token-efficiency` with your task. |
| VS Code Copilot | Open `/skills`, confirm the entry, then use `/token-efficiency`. |
| Gemini CLI | Run `/skills reload`, then `/skills list`; ask it to use `token-efficiency`. |
| Other clients | Use their skill picker or ask: `Use the token-efficiency skill for this task.` |

These controls follow the [Codex](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills), [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills), and [Gemini](https://geminicli.com/docs/cli/skills/) documentation. A mode directive such as `token-efficiency: lean` selects behavior after the skill is loaded; it is not an installation command.

If the skill is missing, check the folder nesting, filename, client version, skill enablement, workspace trust, and the filesystem used by the running agent. Restart the client if discovery has not refreshed. A statement from the model that it is using the skill is weaker evidence than the client's skill list and visible skill-loading event.

## Other Assistants and Hosted Sessions

For an unlisted client, check its Agent Skills documentation or the shared installer's supported-agent list. Do not assume all extensions in VS Code, JetBrains, or another IDE read the same directories.

Where there is no native skill loader, attach or explicitly supply `SKILL.md` with the task and ask the assistant to follow it. This is a manual prompt fallback; persistence, automatic discovery, tools, and usage counters depend on the host. Supplying the full file every turn adds context overhead.

Local installation does not automatically install into hosted chat products or remote agents. Use the host's documented skill upload/plugin mechanism, or commit a supported project skill directory for a hosted repository agent.

## Updates and Removal

Use the installer or client's own management controls for installed skills. For manual copies, compare the source `metadata.version` and contents with your installed copy before replacing it; retain any local customizations. Remove only the chosen installed skill directory when uninstalling. Start a fresh conversation to avoid instructions already loaded into an older session.
