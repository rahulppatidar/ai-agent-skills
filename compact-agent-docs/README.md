# Compact Agent Docs

A portable agent skill for reducing the character and context footprint of Markdown documentation without intentionally changing its material meaning.

It covers agent instructions and skills, project documentation, business documents, and user-created Markdown. Repository-wide discovery combines standard filenames, a complete in-scope Markdown inventory, and link relationships so unlinked custom files are not missed.

## Why this skill exists

Agent-first repositories commonly accumulate verbose instructions, repeated client-specific rules, and overlapping project or business documentation. Files such as `AGENTS.md`, `CLAUDE.md`, and client rules may consume context on every interaction; skills and linked documents consume context when an agent opens them. Unnecessary text competes with the task, code, evidence, and other instructions, which can increase cost, truncation, or missed-constraint risk.

## How it reduces context

The skill:

1. identifies which files are always loaded, path-scoped, or read only on demand;
2. shortens wording and removes only redundancy proven to have no independent purpose;
3. replaces genuine cross-file duplication with a canonical source and reliable pointers when supported by the target clients;
4. moves conditional detail behind explicit triggers so agents load it only when relevant;
5. compacts on-demand project and business documents so they use less context when read.

It reports routine-context reduction separately from on-demand document reduction and total repository size. A smaller Markdown file that no agent reads does not reduce the context window, and moving text into another always-loaded file does not create a saving.

## What it preserves

The workflow keeps requirements, prohibitions, permissions, conditions, exceptions, decisions, rationale, definitions, owners, dates, quantities, commands, paths, links, examples that establish behavior, risks, limitations, attribution, and uncertainty.

It is not ordinary summarization. If equivalence cannot be established, the skill retains the original text or flags it for review instead of deleting it to improve a compression metric.

## Supported documents

- Agent files such as `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, Copilot instructions, and Cursor rules
- Project files such as READMEs, architecture guides, contribution guides, runbooks, ADRs, and documentation trees
- Business files such as PRDs, BRDs, proposals, requirements, policies, SOPs, strategies, roadmaps, meeting notes, and research
- Custom `.md` and `.markdown` files, whether linked or unlinked

Legal, regulatory, signed, generated, vendored, and archival records default to audit-only because their exact wording may be authoritative.

## Prerequisites

The instructions require an agent that can read and edit files. Python 3.9 or later is optional but recommended for the bundled inventory and structural-comparison helper. Git is optional but recommended for preserving and reviewing baselines. The skill has no third-party runtime dependency or network requirement.

The skill does not install or configure Python, Git, package managers, or system software. If an optional tool is unavailable, the agent uses the documented manual fallback without asking the user to install it. Installation can occur only when the user separately requests it and approves a specific plan.

## Installation

When the skill is available on the repository's default branch, run this from the project where you want to use it:

```bash
npx skills add rahulppatidar/ai-agent-skills --skill compact-agent-docs --full-depth
```

Select the desired clients; add `--global` for personal installation. To install from a local checkout before publication:

```bash
npx skills add ./compact-agent-docs
```

Manual locations:

| Client | Project | Personal | Invoke |
| --- | --- | --- | --- |
| Codex | `.agents/skills/compact-agent-docs/` | `~/.agents/skills/compact-agent-docs/` | `$compact-agent-docs` |
| Claude Code | `.claude/skills/compact-agent-docs/` | `~/.claude/skills/compact-agent-docs/` | `/compact-agent-docs` |
| Cursor | `.agents/skills/compact-agent-docs/` or `.cursor/skills/compact-agent-docs/` | `~/.cursor/skills/compact-agent-docs/` | `/compact-agent-docs` or the skill picker |
| GitHub Copilot | `.agents/skills/compact-agent-docs/` or `.github/skills/compact-agent-docs/` | `~/.agents/skills/compact-agent-docs/` or `~/.copilot/skills/compact-agent-docs/` | `/compact-agent-docs` where supported, or ask Copilot to use it |

Copy the complete folder so `SKILL.md`, `references/`, and `scripts/` stay together. Installation only makes the skill discoverable; it does not modify documentation automatically. For example, from the directory containing this repository on macOS or Linux:

```bash
mkdir -p ~/.agents/skills
cp -R -i ./ai-agent-skills/compact-agent-docs ~/.agents/skills/
```

On Windows PowerShell:

```powershell
$source = Resolve-Path .\ai-agent-skills\compact-agent-docs
$parent = Join-Path $env:USERPROFILE '.agents\skills'
$destination = Join-Path $parent 'compact-agent-docs'
New-Item -ItemType Directory -Force -Path $parent | Out-Null
if (Test-Path $destination) { throw 'compact-agent-docs already exists; review it before replacing it.' }
Copy-Item -Recurse -Path $source -Destination $destination
```

Install into the filesystem of the running environment for WSL, containers, remote SSH workspaces, and hosted agents; a host installation is not automatically visible inside them. If a client does not support Agent Skills, attach `SKILL.md` and its relevant references to the task as a manual fallback; automatic discovery is then unavailable.

## Usage

Invoke the skill by itself to compact agent-related documentation in the current repository:

```text
$compact-agent-docs
```

With no path or mode, the skill resolves the current repository root, inventories it, and applies conservative compaction to clearly agent-facing files such as `AGENTS.md`, `CLAUDE.md`, client rules, `SKILL.md` entrypoints, and operational documents they directly reference. It reports the inferred scope before editing. It asks for a path only when no agent-facing file is found, the root cannot be resolved, or candidate inclusion is materially ambiguous; it does not silently expand the default into all project or business Markdown.

Audit before making changes:

```text
$compact-agent-docs Audit the Markdown documentation in this repository. Include
business and custom documents, but do not edit anything. Show which files are
standard, linked, unlinked, exact-sensitive, or likely always loaded.
```

Compact an explicit set:

```text
$compact-agent-docs Compact AGENTS.md, docs/product-prd.md, and docs/policy.md.
Reduce characters without changing material meaning. Leave any uncertain passage
unchanged and report the preservation checks and before/after measurements.
```

Expected result: the agent inventories the scope, protects a baseline, creates a meaning ledger, makes conservative edits, performs source-to-output and output-to-source checks, and reports measurements and uncertainties. It does not claim guaranteed losslessness merely because automated checks pass.

The helper can also be run directly:

```bash
python3 scripts/doc_guard.py inventory /path/to/repository
python3 scripts/doc_guard.py compare /tmp/original.md docs/compacted.md --strict
```

## Verify and troubleshoot

Start a new session, open the client's skill list or picker, and confirm `compact-agent-docs` appears. Explicitly invoke it for the first audit. If it is absent:

- confirm the final path ends with `compact-agent-docs/SKILL.md` and there is no extra nesting;
- confirm `SKILL.md` uses that exact capitalization and the client version supports Agent Skills;
- install into the remote, WSL, container, or hosted filesystem where the agent actually runs;
- restart or reload the client after installation;
- avoid duplicate copies in multiple supported roots, which can make updates ambiguous.

If Python is unavailable, the agent can still follow the semantic workflow and perform manual inventory and diff checks; it must report that the helper was not run. Windows and macOS execution and live installation in the four clients remain untested for version 1.2.

## Limitations

Natural-language semantic equivalence cannot be proven completely by a script or language model. The bundled helper finds structural and protected-literal risks; it explicitly does not certify meaning. Domain owners should review high-impact legal, compliance, policy, contractual, financial, or approved business documents.

Shorter character count does not always mean fewer model tokens. Progressive disclosure can reduce normal context loading without reducing total repository size. Token claims require measurement with a named tokenizer and comparable loading behavior.

Client discovery paths and import behavior differ. The core `SKILL.md` follows the Agent Skills format, but automatic activation is available only in compatible clients and surfaces.

## Validation status

Version 1.2 is at the `review` stage. See [VALIDATION.md](VALIDATION.md) for tested behavior and remaining gaps.

## Author and license

Rahul Patidar. Licensed under [GPL-3.0-only](https://www.gnu.org/licenses/gpl.en.html).
