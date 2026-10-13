# Document discovery and classification

Use this reference for repository-wide, directory-wide, or otherwise multi-file compaction. A standard filename is a discovery signal, not proof that a file is loaded by every client.

## Discovery order

1. Resolve the root and any repository instructions governing it. When the user supplies no path, use the current Git worktree root, or otherwise the current workspace or working directory; never search above it.
2. Inventory all in-scope `.md` and `.markdown` files. Include `.mdc` and similar Markdown-compatible rule files only when the request or client scope includes them.
3. Exclude build output, dependency trees, caches, vendored content, and generated documentation unless the user includes them.
4. Classify each candidate using the groups below.
5. Parse local links and explicit include/import syntax to build relationships.
6. Retain unlinked files in the inventory. An orphan may be intentional, newly created, or loaded directly by a client.

Do not start from links alone: they cannot reveal orphaned documents, path-based client discovery, or files referenced by configuration rather than Markdown.

## Default agent-document scope

For an explicit invocation with no path or task details, discover before asking a question. The default edit scope is:

- standard agent-facing and always-loaded candidates listed below;
- `SKILL.md` entrypoints and agent resource Markdown under client-specific skill directories;
- directly referenced local documents needed to preserve the operational meaning of those files.

Keep nested instruction files and different clients' rules in separate applicability groups even when compacting them together. Do not automatically add ordinary READMEs, business documents, or every Markdown file in the repository. Inventory may reveal them, but they enter the edit scope only when the user requests them or an agent-facing file depends on them.

If the set is non-empty and clearly agent-facing, state the root and candidate paths and continue. Ask only if there is no such candidate, the repository root cannot be determined, or a candidate's inclusion is materially ambiguous. When no standard candidate exists, list likely custom candidates so the user can choose from evidence rather than supply a path blindly.

## Common standard files

### Agent-facing and always-loaded candidates

- `AGENTS.md`, nested `AGENTS.md`, and `AGENTS.override.md`
- `CLAUDE.md` and `CLAUDE.local.md`
- `GEMINI.md`
- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `.cursor/rules/*.mdc`
- other client rule or memory files documented by the repository

Whether these are actually loaded, inherited, imported, or path-scoped is client-specific. Verify the repository's supported clients before replacing content with links or imports.

### Skills and reusable agent resources

- `SKILL.md`
- skill `references/**/*.md`, templates, examples, and setup guides
- `.agents/**/*.md`, `.claude/**/*.md`, `.github/skills/**/*.md`, and client-equivalent skill locations

### Project and community documentation

- `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, and `DEVELOPMENT.md`
- `SECURITY.md`, `SUPPORT.md`, `GOVERNANCE.md`, and `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`, `ROADMAP.md`, release notes, migration guides, and ADRs
- `docs/**/*.md`, issue or pull-request templates, runbooks, and operational guides

### Business and organizational documentation

Names vary; classify by content as well as filename:

- PRDs, BRDs, requirements, specifications, and acceptance criteria;
- strategies, roadmaps, project plans, charters, and briefs;
- proposals, RFCs, ADRs, and decision records;
- policies, standards, procedures, SOPs, controls, and playbooks;
- research, customer findings, meeting notes, onboarding, and training documents;
- budgets, KPI definitions, risk registers, and status reports stored as Markdown.

### Custom documents

Treat any other in-scope Markdown as user-created documentation. Use its content, incoming links, location, frontmatter, and nearby configuration to infer purpose. Do not discard it because its name is unfamiliar or it has no inbound link.

## Exact-sensitive and excluded material

Default to audit-only for licenses, legal terms, privacy notices, regulatory text, signed or formally approved records, audit evidence, immutable minutes, published quotations, generated API references, vendored documentation, and historical changelogs. Some business documents fall into this group.

Record why a path was excluded. Do not count excluded files as compacted.

## Link graph rules

Recognize at least:

- Markdown links and images: `[label](path)` and `![alt](path)`;
- reference-style link definitions;
- wiki links such as `[[path]]` where the repository uses them;
- explicit client imports such as `@AGENTS.md` when documented for that client;
- relative paths named in agent instructions even when they are formatted as code.

Separate external URLs, local files, anchors, and generated routes. Resolve relative file links from the containing document. Preserve anchors when headings change, or update every known inbound reference.

A pointer is safe only when its consumer can follow it, its target is distributed with the source, and its wording tells the agent when the target is relevant.

## Inventory helper

Run from the installed skill directory or use its absolute path:

```bash
python3 scripts/doc_guard.py inventory <root>
python3 scripts/doc_guard.py inventory <root> --json
```

The helper discovers Markdown, classifies likely roles, reports counts and local links, and identifies missing local targets. Review its classification manually; custom naming and client behavior cannot be inferred reliably from filenames alone.
