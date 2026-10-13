---
name: compact-agent-docs
description: Compact Markdown documentation in agent-first repositories while preserving its material meaning and operational behavior. Use when reducing the character or context footprint of AGENTS.md, CLAUDE.md, SKILL.md, READMEs, project documentation, or business documents such as PRDs, BRDs, policies, SOPs, proposals, and decision records. Discover standard and user-created linked or unlinked files, remove only proven redundancy, validate source-to-output coverage, and flag uncertain changes instead of silently dropping content. Do not use for summarization that is allowed to omit detail.
license: GPL-3.0-only
metadata:
  version: "1.2"
  stage: "review"
  owner: "Rahul Patidar"
  author: "Rahul Patidar"
---

# Compact Agent Docs

Reduce the footprint of Markdown and Markdown-compatible agent documents without changing their material meaning.

Compaction is not summarization. A shorter file is successful only when a reader or agent can recover the same requirements, decisions, qualifications, and operational behavior from it. If that cannot be established, keep the original wording or report the uncertainty.

## Why this matters

Agent-first repositories often accumulate repeated instructions, verbose operating guidance, and copies adapted for different clients. Always-loaded files consume context on every turn; referenced documents consume it when opened. Unnecessary content competes with the user's task, code, evidence, and other instructions, and can increase truncation or missed-constraint risk.

Reduce context use by shortening always-loaded documents, replacing proven cross-file duplication with reliable canonical pointers, moving conditional detail behind explicit on-demand triggers, and compacting documents that agents actually read. Do not equate smaller repository size with context savings: identify how each file is loaded and report routine-context, on-demand, and total-size effects separately.

## Material meaning

Preserve every source element that can affect interpretation or action, including:

- obligations, prohibitions, permissions, priorities, and precedence;
- audience, scope, conditions, exceptions, alternatives, and sequences;
- decisions, rationale that constrains later decisions, and unresolved conflicts;
- owners, approvals, status, dates, deadlines, quantities, units, thresholds, and identifiers;
- definitions, acceptance criteria, examples that establish behavior, risks, limitations, and open questions;
- commands, paths, configuration keys, code, links, citations, attribution, and stated uncertainty.

Voice, sentence structure, headings, and layout may change only when they do not carry meaning. Preserve deliberate repetition when it serves safety, emphasis, independent usability, or separate audiences.

## Modes and authorization

Infer the mode from the request:

- **Audit**: inventory documents, identify opportunities and risks, and propose changes without editing.
- **Apply**: compact the explicitly requested scope, then validate it. A request to compact, shorten, optimize, or rewrite the documents authorizes Apply for that scope.

Do not expand a named-file request into repository-wide edits. When the user requests "the docs" or another unclear broad set, inventory first and identify the proposed scope before editing files whose inclusion would materially change the result.

An explicit invocation with no path, root, mode, or other instruction defaults to Apply for the automatically discovered agent-document scope in the current repository. Do not ask the user to name a file before performing discovery. State the inferred root and scope before editing, then proceed unless inclusion is materially ambiguous. A bare invocation does not authorize project, business, legal, generated, or other general Markdown outside that default scope.

Treat legal terms, licenses, regulatory or compliance text, signed or approved records, generated or vendored files, archival logs, and published quotations as exact-sensitive. Audit them by default. Rewrite them only when the user explicitly includes them and equivalence can be reviewed; otherwise preserve them verbatim or exclude them with an explanation.

Never stage, commit, publish, or delete originals unless separately requested.

## Runtime dependencies

The core workflow requires only the host agent's file-reading and editing capabilities. Python 3.9 or later enables the bundled helper, and Git can provide a recoverable baseline, but both are optional.

Check whether optional tools already exist before using them. Do not install, upgrade, or configure Python, Git, package managers, or system software for this skill. If Python is unavailable, perform inventory and comparison manually; if Git is unavailable, use temporary snapshots outside the deliverable tree. Install an optional tool only when the user separately requests it and approves a specific installation plan.

## Workflow

### 1. Establish the objective and measurement

Determine the requested scope and whether the user wants fewer characters, fewer tokens, less always-loaded context, less duplication, or a combination. If no measurement is specified, optimize for fewer characters and less routine context where safe, then report those as separate outcomes. Do not ask the user to choose a measurement merely because it was omitted.

Characters, bytes, words, and tokens are different measures. Report token reduction only when measured with an identified tokenizer. Moving detail behind a conditional reference may reduce routine context while leaving total repository size unchanged; label these separately.

### 2. Discover documents before editing

For a named file, inspect that file and the documents it directly depends on. For repository, directory, omitted, or unclear multi-file scope, read [references/discovery.md](references/discovery.md), then:

1. inventory all in-scope `.md`, `.markdown`, and requested Markdown-compatible rule files;
2. classify standard agent, project, business, exact-sensitive, generated, and custom documents;
3. extract local Markdown links, wiki links, and explicit include/import pointers;
4. build inbound and outbound relationships and report broken targets;
5. include unlinked user-created files in the inventory rather than assuming the link graph is complete.

Use `python3 scripts/doc_guard.py inventory <root>` when Python is available. Its output is evidence for discovery, not authority about scope or meaning.

When no path or root is supplied:

1. use the current Git worktree root when one exists; otherwise use the current workspace or working directory;
2. do not scan above that root or include the installed copy of this skill unless it is inside the target repository;
3. select standard agent instructions, client rule or memory files, reusable `SKILL.md` files, and local documents they directly reference for their operational meaning;
4. include all clearly agent-facing candidates when several clients or nested scopes are present, but keep their applicability boundaries distinct;
5. exclude ordinary project and business Markdown from the default edit scope unless it is a necessary dependency of an agent-facing document.

If this produces a coherent non-empty set, identify it and continue without asking for a path. Ask for direction only when the root cannot be resolved, no agent-facing candidate exists, or including an ambiguous candidate would materially change the result. In the no-candidate case, report what was searched and show any likely custom candidates before asking.

### 3. Preserve a recoverable baseline

Before editing, ensure the original content is recoverable from version control or a temporary snapshot outside the deliverable tree. Include untracked files in that protection. Do not assume `HEAD` contains the user's current version, and do not overwrite unrelated working-tree changes.

### 4. Build a preservation ledger

Read [references/preservation.md](references/preservation.md). Decompose each source document into atomic meaning units and assign stable temporary IDs. For each unit record its source location, kind, exact-sensitive literals, and intended destination.

The ledger may stay in working notes or a temporary file. Do not add it to the repository unless requested. Preserve contradictions as separate units; do not silently reconcile them.

### 5. Compact conservatively

Prefer, in order:

1. remove exact repetition that has no independent purpose;
2. merge statements proven to have identical scope, force, conditions, and exceptions;
3. replace wordy phrasing with direct language while retaining modality and qualification;
4. factor genuinely shared material into one canonical location with a precise pointer from every consumer;
5. move conditional detail behind an explicit trigger when the target agents load it on demand.

Do not:

- replace precise language with abbreviations, symbols, or telegraphic fragments that require guessing;
- weaken `must` into `should`, permission into obligation, or a qualified rule into an absolute one;
- collapse examples that define distinct boundary cases;
- convert prose to tables merely because tables look shorter;
- remove rationale that limits future decisions or warnings whose repetition is intentional;
- use an import or link unless the intended clients actually follow it in that context;
- claim context savings from a file that is not normally loaded into context.

Keep the smallest clear edit. A file with no safe reduction may remain unchanged.

### 6. Verify equivalence in two directions

Perform both passes against the baseline:

1. **Source to compacted**: map every ledger unit to explicit equivalent text or a valid, discoverable canonical reference.
2. **Compacted to source**: confirm every output claim is supported by the source and no conflict was accidentally resolved.

Then check document-specific invariants from `references/preservation.md`. When Python is available, run:

```bash
python3 scripts/doc_guard.py compare <original-file> <compacted-file> --strict
```

The helper checks structural and literal risks only. A passing result does not prove semantic equivalence; the ledger and bidirectional review remain required.

If a material unit is missing, ambiguous, or only implied, restore it or leave the source unchanged. Do not accept a semantic regression to reach a numeric target.

### 7. Report the result

For Apply mode, report:

- files changed, unchanged, excluded, and needing review;
- characters and bytes before and after, plus the percentage when comparable;
- separately measured token or routine-context changes, if any;
- preservation checks performed and any unresolved uncertainty;
- broken links or pre-existing contradictions discovered.

For Audit mode, provide the inventory, highest-value opportunities, exact-sensitive exclusions, expected measurement type, and a proposed edit scope. Do not promise a reduction before inspecting the material.

## Completion criteria

The task is complete only when:

- every material source unit remains explicit or is reached through a reliable pointer;
- the compacted text adds no unsupported requirement, decision, or factual claim;
- protected literals and Markdown structure have been checked;
- links and references affected by the edit still resolve;
- the result is shorter by the requested measure, or the report explains why no safe reduction was possible;
- limitations and unreviewed files are disclosed without claiming guaranteed losslessness.
