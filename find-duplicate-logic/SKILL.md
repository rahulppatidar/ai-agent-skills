---
name: find-duplicate-logic
description: Find existing code that duplicates or substantially overlaps the behavior of a target implementation, current diff, or requested feature. Use before implementing new logic, while reviewing a change, or when investigating whether business rules have been implemented more than once. Compare behavior rather than syntax, distinguish true duplication from harmless similarity, cite concrete code locations, and do not refactor automatically. Do not use for byte-level or textual duplicate-file detection.
license: GPL-3.0-only
metadata:
  version: "1.0"
  stage: review
  owner: Rahul Patidar
  author: Rahul Patidar
---

# Find Duplicate Logic

## Purpose

Determine whether a repository already contains logic that is behaviorally equivalent to, or substantially overlaps with, a target behavior.

The target may be:

- a file, function, class, method, component, query, job, handler, or module;
- the current working-tree or staged diff;
- a natural-language behavior the developer is about to implement;
- a code snippet supplied by the user.

This skill answers one question:

> Does this behavior already exist somewhere else in the repository?

It is **not** a generic duplicate-code detector. Textual similarity is weak evidence. The goal is to detect duplicated **rules, decisions, calculations, transformations, side effects, validation, state transitions, and workflows**, even when names and syntax differ.

## When to use

Use this skill when the user asks things such as:

- "Does this already exist?"
- "Find duplicate logic."
- "Am I reimplementing something?"
- "Search for equivalent behavior before I add this."
- "Check my diff for duplicated business logic."
- "Is there another function that does the same thing?"
- "Find overlapping implementations."

It is particularly valuable **before implementation** and **before review/commit**.

## What this skill is not

Do not use this skill primarily to:

- find copy-pasted text or token-level clones;
- find code that merely uses the same framework or design pattern;
- enforce DRY mechanically;
- perform a broad architecture review;
- refactor or consolidate code automatically;
- claim two implementations are duplicates based only on names;
- recommend a shared abstraction merely because two blocks look similar.

If two pieces of code have similar structure but represent different domain rules, classify them as **similar, not duplicate**.

## Operating modes

Infer the mode from the user's request.

### 1. Target mode

The user points to existing code.

Example:

> Find duplicate logic for `calculateRefund()`.

Analyze the target first, derive its behavior, then search for equivalent behavior elsewhere.

### 2. Diff mode

The user asks whether their current changes introduce duplicated logic.

Example:

> Check my diff for duplicate logic.

Inspect changed behavior, not every changed line. Search the existing repository for earlier implementations.

### 3. Intent mode

The user describes behavior they are about to implement.

Example:

> Before I add prorated refunds, check whether we already do this somewhere.

Turn the request into a behavioral signature, then search the repository before suggesting implementation.

## Core workflow

Follow these steps in order.

### Step 1: Establish the target

Identify exactly what behavior is being checked.

For code targets, read enough surrounding code to understand:

- inputs;
- outputs;
- predicates and branching rules;
- calculations;
- state transitions;
- persistence behavior;
- externally visible side effects;
- error handling;
- boundary conditions;
- important dependencies;
- callers/callees when they change the meaning of the logic.

For a diff, separate behavior changes from renames, formatting, generated files, and mechanical edits.

For a natural-language request, restate it internally as deterministic behavior rather than implementation details.

If the target cannot be identified or inspected, do not guess. State exactly what is missing and ask one focused question. If part of the target is inspectable, analyze that portion and disclose the limitation.

### Step 2: Build a behavioral signature

Summarize the target as a compact set of behaviors. Do **not** search only for its function or variable names.

A useful behavioral signature may include:

- domain nouns and synonyms;
- verbs/actions;
- key predicates;
- formulas or transformations;
- constants, thresholds, statuses, and enum transitions;
- validation rules;
- error conditions;
- read/write entities;
- side effects;
- library/API calls that strongly indicate the behavior.

Example:

Target code named `eligibleForAdultPlan()` might yield:

- accepts customer/user;
- requires age >= 18;
- requires country == IN;
- returns eligibility boolean.

Search for combinations of those concepts, not only `eligibleForAdultPlan`.

### Step 3: Search broadly, then narrow

Use repository search tools available in the host agent.

Search in multiple passes where appropriate:

1. exact identifiers and domain terms;
2. synonyms and related domain concepts;
3. constants, enum values, error messages, database fields, route names;
4. key predicates or calculations;
5. reads/writes to the same entities;
6. callers of shared dependencies;
7. tests that describe the same behavior in different words.

Do not stop after the first plausible match. Search enough of the repository to compare credible candidates.

Stop when the behavioral signature has been compared against credible candidates and the relevant application, domain, and test areas have representative coverage. Report material exclusions, unreadable paths, or search failures rather than silently broadening the task indefinitely.

Prioritize application code, domain code, services, jobs, handlers, validators, queries, and tests. Treat generated code, vendored code, build output, lockfiles, and snapshots as low-value unless the target specifically concerns them.

### Step 4: Read candidate implementations in context

For each credible candidate, inspect enough surrounding code to compare behavior accurately.

Check:

- same inputs, or equivalent inputs represented differently;
- same decision conditions;
- same result;
- same side effects;
- same failure behavior;
- same domain meaning;
- meaningful differences in scope or policy.

Do not infer equivalence from a search-result snippet alone.

### Step 5: Classify each candidate

Use exactly these categories.

#### A. Exact duplicate

The implementations encode effectively the same behavior with no meaningful domain difference.

Examples:

- the same validation rule copied into two services;
- the same calculation reimplemented with renamed variables;
- a function copied and lightly reformatted.

#### B. Semantic duplicate

The implementations are syntactically different but enforce the same domain rule or produce equivalent behavior.

Example:

```ts
user.age >= 18 && user.country === 'IN'
```

and

```ts
customer.country === 'IN' && customer.age > 17
```

may be semantic duplicates if they represent the same eligibility rule.

#### C. Partial overlap

They share a meaningful subset of behavior but differ in policy, scope, side effects, or boundary conditions.

Do not recommend consolidation by default.

#### D. Similar, not duplicate

They look structurally similar or use the same technical pattern but represent different domain behavior.

Examples:

- two CRUD handlers;
- two React forms;
- two validators with unrelated rules;
- two queue consumers with the same skeleton but different business decisions.

### Step 6: Assign confidence

For each finding, assign one of:

- **High** — evidence strongly supports behavioral equivalence or overlap;
- **Medium** — likely, but one or more material details remain uncertain;
- **Low** — noteworthy resemblance, insufficient evidence for duplication.

Confidence must reflect evidence, not severity.

### Step 7: Recommend the least risky action

Recommendations must be conservative.

Possible actions:

- reuse the existing implementation;
- call an existing domain service/helper;
- move a shared rule to an existing owner;
- extract a common primitive **only when a stable shared concept exists**;
- leave implementations separate because the overlap is incidental;
- investigate an identified behavioral difference before changing anything.

Never propose abstraction solely to reduce line count.

When two implementations may evolve independently, prefer keeping them separate.

### Step 8: Report findings with evidence

Every reported duplicate must name concrete source locations and explain **why** the behavior overlaps.

Prefer file paths plus function/class/method names and line ranges when available.

Do not report vague statements such as "this seems duplicated elsewhere."

## Evidence rules

A strong duplicate finding should usually have at least two independent points of behavioral evidence, for example:

- same condition + same outcome;
- same calculation + same boundary behavior;
- same database mutation + same prerequisite;
- same state transition + same failure rule;
- same rule expressed in tests and implementation.

Names alone are not evidence.

Shared dependencies alone are not evidence.

Matching AST/code shape alone is not sufficient evidence of semantic duplication.

## Important false-positive checks

Before calling something a duplicate, ask:

1. Do these pieces of code belong to the same domain concept?
2. Would changing the business rule require changing both?
3. Are their boundary conditions actually the same?
4. Are their side effects the same?
5. Are differences intentional because the callers have different policies?
6. Would sharing the implementation couple modules that should remain independent?

If the answer to 1 or 2 is no, the code is usually not duplicate business logic.

## Domain ownership test

When duplication is found, identify the likely owner of the rule.

Prefer reusing logic from the module that owns the domain concept rather than whichever implementation happens to be older.

Evidence for ownership can include:

- module/package boundaries;
- public API names;
- domain entities;
- tests;
- documentation;
- call direction;
- persistence ownership.

Do not automatically declare the first implementation canonical.

## Tests are evidence

Tests often reveal semantic duplication better than implementation search.

Look for tests describing:

- the same Given/When/Then scenario;
- the same edge cases;
- the same state transition;
- the same expected error;
- the same numeric outcome.

If two implementations have superficially similar code but different tests, investigate before labeling them duplicates.

## Output contract

Lead with the bottom line. Keep the result concise when no duplication is found and provide more detail only for credible findings.

Include:

- the target and its behavioral signature;
- each candidate's category, confidence, and concrete source locations;
- shared behavior and material differences;
- the evidence supporting the classification;
- the least risky suggested action;
- important search coverage and limitations.

When there are multiple credible candidates or the user requests a standalone report, read and adapt [the report template](references/report-template.md). Do not add empty sections merely to follow the template.

## Diff-mode additions

When analyzing a diff:

- inspect staged changes, unstaged changes, and relevant untracked files if the host environment exposes them and the user did not narrow the request;
- identify newly introduced behaviors rather than scanning only added lines;
- compare each new behavior against the pre-existing codebase;
- ignore pure formatting, comments, generated output, and mechanical renames unless they conceal behavior changes;
- explicitly note when the diff merely calls existing logic rather than duplicating it.

## Intent-mode additions

When the user has not written code yet:

- derive a behavioral signature from the requested feature;
- search for existing implementations, utilities, rules, and tests;
- report what can be reused before discussing new code;
- do not invent a new architecture unless the user asks for implementation advice.

## Language/framework neutrality

This skill is repository- and language-agnostic.

Adapt searches to the project:

- TypeScript/JavaScript: exported functions, services, hooks, handlers, schemas, validators;
- Python: functions, classes, serializers, services, model/query logic;
- Go: package functions, methods, interfaces, handlers;
- Rust: functions, impl blocks, traits, match branches;
- Java/Kotlin/C#: services, domain methods, validators, repositories;
- SQL: equivalent filters, joins, calculations, constraints, views, procedures;
- frontend: business rules, state transitions, transformations, not merely component structure;
- infrastructure: repeated policy, permissions, routing, retry, scaling, or resource rules.

## Guardrails

- **Do not edit code unless explicitly asked.** This skill is diagnostic by default.
- **Do not manufacture duplication.** "No meaningful duplicate found" is a valid and useful result.
- **Do not enforce DRY as an absolute rule.** Some duplication is cheaper and safer than coupling.
- **Do not treat tests as duplicate production logic.** Tests can repeat business rules intentionally; use them as evidence.
- **Do not collapse policy differences.** A one-character threshold difference may be the entire business requirement.
- **Do not ignore negative behavior.** Error paths and "do nothing" branches can distinguish otherwise similar code.
- **Do not call two wrappers duplicates** when they intentionally adapt the same primitive for separate modules.
- **Do not recommend a new shared abstraction** unless the shared concept has a stable name and ownership.

## Quality bar

A good run lets a developer answer:

1. What exact behavior did we search for?
2. Where else does that behavior exist?
3. How equivalent are the implementations?
4. What differences matter?
5. How confident are we?
6. Should we reuse, consolidate, investigate, or leave them separate?

If the report cannot answer those questions with concrete repository evidence, continue investigating before concluding.

## Additional references

- Read [the detection guide](references/detection-guide.md) when candidate evidence is ambiguous or a classification needs a dimension-by-dimension comparison.
- Read [the report template](references/report-template.md) only for a multi-finding or explicitly requested standalone report.
