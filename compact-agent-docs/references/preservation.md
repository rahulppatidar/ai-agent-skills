# Semantic-preservation protocol

Use this reference before applying compaction and during final equivalence review.

## Preservation ledger

Represent every material source unit with:

| Field | Meaning |
| --- | --- |
| ID | Stable temporary identifier, such as `D2-R7` |
| Source | File and heading or line |
| Kind | Requirement, exception, fact, decision, rationale, definition, example, risk, open question, or reference |
| Force | Must, must not, should, may, factual, uncertain, or historical |
| Scope | Audience, component, time, environment, or condition |
| Exact values | Commands, paths, names, dates, numbers, units, URLs, quotations, or code |
| Destination | Equivalent output text or reliable canonical pointer |
| Status | Preserved, intentionally verbatim, uncertain, or excluded with reason |

Split compound sentences when their clauses have different scope or force. Keep contradictory units separate and visible.

## Equivalence tests

For each proposed merge or rewrite, ask:

1. Does it retain the same actor and audience?
2. Does it apply to the same objects, files, products, and environments?
3. Are obligation, permission, recommendation, and prohibition unchanged?
4. Are all preconditions, exceptions, alternatives, orderings, and stop conditions present?
5. Are quantities, units, dates, owners, identifiers, commands, paths, links, and code exact?
6. Does it preserve uncertainty, lifecycle status, evidence level, and known limitations?
7. Would a reasonable agent or person take the same action in every covered case?

If any answer is unknown, the rewrite is not established as equivalent.

## Document-specific invariants

### Agent instructions and skills

Preserve instruction priority, directory scope, trigger conditions, authorization boundaries, required tools, execution order, stop conditions, validation, output contracts, exceptions, and distinctions between recommendations and requirements. Verify that any new pointer loads in every claimed client.

### Product and business requirements

Preserve problem and goal, non-goals, users, use cases, functional and non-functional requirements, acceptance criteria, dependencies, assumptions, constraints, milestones, metrics, owners, approvals, risks, open questions, and decision status. Keep requirement identifiers stable when other artifacts may reference them.

### Policies, controls, and procedures

Preserve applicability, responsible roles, mandatory versus advisory language, control frequency, evidence, escalation, exceptions, approvals, retention periods, and enforcement. Treat legal or regulatory language as exact-sensitive.

### Proposals, strategies, and decisions

Preserve alternatives, evaluation criteria, tradeoffs, chosen decision, rejected options when their rationale constrains reconsideration, consequences, owner, status, and review date.

### Meeting notes and research

Preserve attribution, observed facts versus interpretation, decisions, action items, owners, deadlines, dissent, sample limitations, citations, and unanswered questions. Do not turn a participant statement into an organizational decision.

### Technical and operational documentation

Preserve prerequisites, supported versions and environments, commands, ordering, failure behavior, rollback, safety warnings, expected results, paths, configuration, and troubleshooting branches.

## Bidirectional review

After editing:

- Walk the ledger from source to output. No material unit may be absent or merely implied.
- Walk every output statement back to a ledger unit. Compression must not invent policy, certainty, causality, or consensus.
- Re-read the compacted document without relying on memory of the source. Confirm it remains independently usable for its intended audience.
- Inspect the actual diff and affected inbound links.

Automated checks can find missing literals, malformed fences, and broken links. They cannot prove that two natural-language statements have the same meaning.

## Reporting confidence

Use these labels for any unresolved transformation:

- **Verified**: bidirectional mapping and relevant structural checks pass.
- **Review needed**: likely equivalent, but domain, legal, or stakeholder judgment is required.
- **Not compacted**: equivalence was not established, so the original was retained.

Do not use “lossless” or “100% preserved” as an unqualified claim. State the checks and scope that support the result.
