# Production Readiness Review

A reusable AI engineering skill for reviewing whether a feature, service, API, infrastructure change, or application is ready for production.

## What it does

This skill reviews production readiness across areas such as:

- deployment safety
- rollback and recovery
- observability
- reliability
- performance and capacity
- security and privacy
- database safety
- external dependencies
- operational readiness
- testing evidence

The result is a structured production-readiness decision with risks, blockers, unknowns, deployment checks, and rollback checks.

## When to use it

Use this skill before releasing:

- a new feature
- a new API
- a new microservice
- a major code change
- a database migration
- an infrastructure change
- a third-party integration
- a high-risk production change

It is especially useful when the team is asking:

> Are we actually ready to ship this?

## When not to use it

This skill is not a replacement for:

- code review
- security testing
- penetration testing
- load testing
- infrastructure inspection
- business acceptance testing
- human release approval

It can identify risks and missing evidence, but it cannot prove that a system is safe for production.

## Files

```text
production-readiness-review/
├── SKILL.md
└── README.md
```

`SKILL.md` contains the instructions the AI assistant follows.

`README.md` explains the skill to developers and maintainers.

## Installation

For Codex, Copilot, Cursor, Gemini CLI, Windsurf, Cline, OpenCode, Antigravity, Junie, and Windows setup, see the shared [installation guide](../INSTALLATION.md). Substitute `production-readiness-review` for the example skill name. Claude Code examples follow.

### Claude Code — personal skill

Copy the folder to:

```text
~/.claude/skills/production-readiness-review/
```

The final structure should be:

```text
~/.claude/skills/
└── production-readiness-review/
    ├── SKILL.md
    └── README.md
```

### Claude Code — repository skill

For a skill shared by a project team, place it under:

```text
.claude/skills/production-readiness-review/
```

Example:

```text
my-project/
├── .claude/
│   └── skills/
│       └── production-readiness-review/
│           ├── SKILL.md
│           └── README.md
└── ...
```

Commit the directory to the repository if the team should share the same skill.

## Usage

Ask the assistant to use the skill on the feature or change you are preparing to release.

Example:

```text
Use the production-readiness-review skill on this feature.

Feature:
Payment retry service

Environment:
Kubernetes

Database:
PostgreSQL

Expected traffic:
500 requests per second

Review the implementation, deployment configuration,
database migration, tests, monitoring and rollback plan.
```

You can also use a shorter request:

```text
Run a production readiness review on this change.
```

Provide as much real evidence as possible, including:

- requirements
- architecture
- implementation
- configuration
- deployment manifests
- database migrations
- tests
- monitoring configuration
- expected traffic
- external dependencies
- rollback plan

The quality of the review depends on the evidence available.

## Expected output

The skill should return one of four decisions:

```text
READY
READY WITH CONDITIONS
NOT READY
INSUFFICIENT INFORMATION
```

It should also identify:

- release blockers
- high-risk findings
- unknowns
- deployment actions
- rollback actions
- post-deployment verification steps

## Example finding

```text
Severity: High
Area: Reliability

Finding:
The payment provider request has no timeout.

Evidence:
PaymentClient.send() waits on the HTTP client default timeout.

Failure scenario:
If the payment provider becomes slow, application workers may
remain occupied until the connection is terminated, eventually
exhausting the worker pool.

Recommendation:
Configure explicit connection and request timeouts and define
retry behaviour.

Release blocker:
Yes
```

## Recommended workflow

For important releases, use this skill after implementation and normal code review.

A practical sequence is:

```text
Requirements
    ↓
Implementation
    ↓
Tests
    ↓
Code Review
    ↓
Production Readiness Review
    ↓
Security / Performance Review when required
    ↓
Release Decision
    ↓
Deployment
    ↓
Post-deployment verification
```

The production-readiness review should not automatically approve or deploy anything. The final release decision remains with the engineer or team responsible for the system.

## Maintenance

Update the skill when real production releases reveal:

- checks that repeatedly catch useful problems
- checks that create unnecessary noise
- missing failure scenarios
- new infrastructure patterns
- new deployment practices
- recurring incident causes

Prefer evidence from real usage over adding more checklist items.

## Version

Initial version: `1.0`

Suggested stage: `Review`

Suggested catalogue situation:

> I am about to release a feature to production.

Suggested limitation:

> Not suitable as a replacement for real load testing, security testing, infrastructure inspection, or human release approval.
