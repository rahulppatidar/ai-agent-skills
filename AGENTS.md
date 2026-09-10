# Repository Instructions

## Purpose and Layout

This repository contains reusable AI agent skills. Each skill lives in a directory named after the skill and has a `SKILL.md` entrypoint with YAML frontmatter and Markdown instructions.

Current skills:

- `production-readiness-review/SKILL.md`: Review release readiness, operational risks, verification evidence, and recovery plans.
- `token-efficiency/SKILL.md`: Reduce total conversation and tool token usage while preserving correctness, safety, usefulness, and completion. Supports Lean, Balanced (default), and Thorough modes.

Human documentation: `README.md` catalogs the skills, `INSTALLATION.md` covers client installation, and `token-efficiency/MEASUREMENT.md` explains optional usage comparisons.

## Authoring References

- When creating or substantially revising a skill, consult the relevant sections of the [Agent Skills specification](https://agentskills.io/specification) for format requirements and [skill-creation best practices](https://agentskills.io/skill-creation/best-practices) for instruction design and evaluation. Reuse sections already retrieved in the current task; do not reload both pages for every minor edit.
- Treat the specification as the format reference and best practices as guidance to apply proportionately. Use vendor documentation for installation, discovery, and client-specific behavior. These references do not override explicit user requirements or higher-priority instructions.
- Review whether the skill adds useful guidance beyond the agent's existing knowledge, has a clear trigger and default workflow, and loads optional detail only when needed. Avoid adding instructions solely to fill a template.
- Validate behavior on representative tasks before claiming stable readiness or effectiveness. Inspect execution traces as well as final outputs; record what was tested and any remaining gaps. For efficiency claims, compare against runs without the skill and include its context overhead.
- If a reference cannot be accessed, use available validated guidance, disclose the limitation, and do not claim a fresh standards check. Keep these authoring references here rather than adding mandatory web lookups to every skill's runtime instructions.

## Creation Checklist

Use this checklist for new skills and substantial behavior changes. Scale validation to risk and scope; do not add boilerplate sections or extra files solely to satisfy the checklist.

- Define the intended tasks, required inputs, expected deliverable, and completion criteria. State how material missing information should be handled.
- Check discovery with representative prompts that should activate the skill and prompts that should not. Distinguish testing the description from explicitly invoking the skill.
- Exercise a representative task, a missing-information case, and relevant failure handling. Check output correctness and completeness, execution traces, unnecessary work, and interaction with other skills when applicable.
- Verify portability: declare necessary dependencies, test executable helpers when present, and ensure runtime references resolve within the installed skill folder without relying on this repository's surrounding files.
- Before release, record tested agents and versions, results, remaining limitations, and evidence supporting the lifecycle stage. Make the applicable license clear when distributing a skill separately. Record checks not performed rather than implying they passed.

## Making Changes

- Read the affected skill before editing it. Preserve unrelated work and existing metadata unless the task requires a change.
- Use lowercase, hyphen-separated directory and skill names. Include `name` and `description` in each new skill's YAML frontmatter.
- Always include a `metadata` mapping in every skill's YAML frontmatter. For new skills, start with:

  ```yaml
  metadata:
    version: "1.0"
    stage: review
    owner: Rahul Patidar
  ```

- Follow the skill format: `name` and `description` are required top-level fields; custom version, stage, and owner fields belong under `metadata`. The version and lifecycle rules here are repository conventions, not requirements of the skill format.
- Store metadata values as strings. Treat version and stage as maintained values, not fixed constants: increment the minor version for compatible instruction or behavior changes and the major version for incompatible workflow or output-contract changes. Pure formatting or metadata relocation does not require a version bump.
- Keep `stage` aligned with actual lifecycle status (for example, `draft`, `review`, `stable`, or `deprecated`). Reassess it when behavior changes; do not promote to `stable` solely because structural validation passes. Preserve the owner unless a change is requested.
- Keep instructions concise, actionable, and self-contained. Add scripts, references, assets, or interface metadata only when they support a concrete need.
- Include a concise human-facing `README.md` alongside each skill in this repository. Explain its purpose, usage, and relevant limitations without copying the full agent instructions. Keep it aligned when behavior changes. This is a repository convention; the skill format only requires `SKILL.md`.
- Maintain shared client setup in `INSTALLATION.md`, with vendor links and a verification date. Distinguish documentation checks from installations actually tested. Keep measured token savings separate from estimates or workflow indicators; never publish percentages without comparable usage evidence. Human documentation changes alone do not require a skill version bump.
- Preserve the skill's intended scope, explicit user requirements, authorization boundaries, and necessary verification.
- Create skills in this repository. Install them into an agent's personal skill directory only when requested.

## Validation

- Check changed skills for valid frontmatter, matching directory/name values, the required `metadata.version`, `metadata.stage`, and `metadata.owner` strings, complete instructions, working referenced paths, and unresolved placeholders.
- When the local skill-creator validator is available, run it for each new or changed skill:

  ```bash
  python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" <skill-directory>
  ```

- The validator checks structure; also review whether the instructions satisfy the requested behavior and preserve constraints. If it is unavailable, perform those checks manually and report that limitation.
- The bundled validator accepts `metadata` but does not validate its contents; check the required metadata fields separately.
- Run `git diff --check` for tracked edits and inspect newly created files as well. Run executable helpers or relevant behavioral checks when changed behavior warrants them.
- The repository currently has no shared automated test suite or build step.

## Keep This File Current

Update this `AGENTS.md` with every repository change before handing work back to the user. Update affected layout, conventions, or validation guidance and add a concise dated entry below describing the final change and its validation status. Group related edits from one task into one entry; updating this file does not require a separate recursive entry.

Keep entries factual. Record checks actually performed and any material limitations. Do not duplicate entire skill instructions or conversation history here.

## Change Record

- 2026-09-10: Refined token-efficiency to version 1.1, retaining stage review. Consolidated overlapping guidance, added an operational decision loop and explicit stop conditions, and preserved total-task-cost and quality requirements. Clarified meta-skill usage in its README with one composition example. Skill validation passed; checked metadata, Markdown structure, local links, and size reduction. Runtime savings and cross-agent behavior remain unmeasured; no benchmarking infrastructure was added.
- 2026-09-10: Documented automatic selection, explicit invocation, and optional persistent project instructions. Added a post-installation setup prompt that verifies skill availability, identifies the current agent's project instruction mechanism, preserves existing rules, and avoids duplicate sections. Checked vendor guidance, local links and headings, and whitespace; the setup prompt was not executed and no runtime configuration or skill behavior changed.
- 2026-09-10: Added explicit Agent Skills specification and best-practices references, plus a creation checklist covering task contracts, trigger checks, behavior, portability, licensing, and release evidence. Reviewed for consistency with the retrieved guidance and repository conventions; the diff passed whitespace checks. Skill behavior and metadata are unchanged; comparative token-efficiency testing remains outstanding before claiming stable readiness or measured savings.
- 2026-09-10: Added shared installation guidance for ten agent families, including Windows, native installers, activation, and the shared installer's `--full-depth` flag for this layout. Expanded the root catalog and linked both skill READMEs. Added a token measurement guide covering usage sources, paired comparisons, quality checks, and unavailable metrics. Checked primary documentation, whitespace in six documents, eleven local links, and syntax of seven Bash examples. PowerShell was reviewed only; no live client installations or savings benchmarks were performed. Skill instructions, version, and stage are unchanged.
- 2026-09-10: Added `token-efficiency/README.md` with human-facing usage, modes, expectations, and maintenance guidance. Established the per-skill README convention. Reviewed against `SKILL.md`; verified relative links and whitespace. Skill behavior and metadata are unchanged.
- 2026-09-10: Moved version, stage, and owner under `metadata` in both skills, with string values. Both skills passed the skill-creator validator and separate metadata checks. Clarified that version increments and lifecycle stages are repository conventions; initial values are defaults, not permanent requirements.
- 2026-09-10: Required `version: 1.0`, `stage: review`, and `owner: Rahul Patidar` in every skill and added them to `token-efficiency`. Parsed both skills' YAML and confirmed the required values. Documented the bundled validator's rejection of these custom top-level fields.
- 2026-09-10: Added `token-efficiency/SKILL.md` with context, tool, output, adaptive-mode, and quality guidance. Passed the skill-creator validator using `python3`; reviewed coverage against the requested eleven sections. Added this root `AGENTS.md` with repository conventions and the requirement to maintain it with every change.
