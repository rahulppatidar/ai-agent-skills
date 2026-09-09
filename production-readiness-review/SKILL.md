---
name: production-readiness-review
description: Review a feature, service, API, infrastructure change, or application before production release. Use when evaluating deployment safety, rollback, observability, reliability, capacity, data safety, external dependencies, testing evidence, and operational readiness.
version: 1.0
stage: review
owner: Rahul Patidar
---

---

# Production Readiness Review

## Purpose

Review a feature, service, API, infrastructure change, or application before production release.

The goal is not only to determine whether the code works. The goal is to determine whether the change can be deployed, operated, observed, recovered, and rolled back safely in production.

## When to use

Use this skill when:

- a feature is ready for release
- a new API or service is being deployed
- a major architecture change is being introduced
- a critical background job is going live
- a new external integration is being released
- infrastructure or configuration is changing
- a change has significant production risk
- a team asks: "Are we ready to ship this?"

Run this review before the final production deployment.

## Do not use this skill for

Do not use this as:

- a replacement for code review
- a replacement for security review
- a replacement for performance or load testing
- proof that a system is production-safe
- a substitute for inspecting the real infrastructure
- a substitute for understanding business requirements

If important production information is unavailable, state that explicitly rather than assuming it.

## Review procedure

Review the proposed change against each section below.

For every finding provide:

- Area
- Finding
- Severity
- Evidence
- Failure scenario
- Recommendation
- Release blocker: Yes or No

Severity must be one of:

- Critical
- High
- Medium
- Low
- Informational

Do not invent missing system information.

Mark unknown information as:

`UNKNOWN — requires verification`

## 1. Functional readiness

Check:

- Are acceptance criteria satisfied?
- Are important edge cases covered?
- Are failure scenarios handled?
- Are inputs validated?
- Are error states defined?
- Are partial failures handled?
- Are retries safe?
- Are operations idempotent where required?
- Is existing behaviour preserved where required?

Identify anything that could pass testing but fail under real production conditions.

## 2. Deployment safety

Check:

- Can the change be deployed without downtime?
- Does deployment order matter?
- Can old and new application versions coexist?
- Are database or schema changes backward compatible?
- Are configuration changes required?
- Are environment variables documented?
- Are secrets required?
- Are dependencies available before deployment?
- Can a partial deployment leave the system inconsistent?
- Are feature flags needed?

Describe the safest deployment order when relevant.

## 3. Rollback and recovery

Check:

- Can the deployment be rolled back?
- What happens to data created by the new version?
- Is rollback compatible with database changes?
- Is configuration rollback possible?
- Can a failed deployment be safely retried?
- Is there a recovery procedure?
- Are irreversible operations identified?

For irreversible changes, explicitly state:

`IRREVERSIBLE CHANGE`

## 4. Observability

Check whether operators can detect and understand failures.

Review:

- application logs
- structured logging
- metrics
- traces
- dashboards
- alerts
- error reporting
- correlation or request IDs
- audit logs where required

For every important failure mode ask:

> How would the team know this happened?

If the answer is unclear, record an observability gap.

## 5. Reliability

Check:

- timeouts
- retry behaviour
- retry limits
- exponential backoff
- circuit breakers
- dependency failures
- connection pool exhaustion
- queue failures
- duplicate processing
- concurrency behaviour
- race conditions
- resource exhaustion
- graceful degradation

Identify single points of failure.

## 6. Performance and capacity

Check:

- expected traffic
- peak traffic
- database load
- query behaviour
- N+1 queries
- CPU usage
- memory usage
- network usage
- connection pools
- queues
- caching
- external API limits
- rate limits

Ask:

> What is likely to become the first bottleneck as usage increases?

If capacity information is unavailable, mark it as unknown.

## 7. Security and privacy

Perform a production-oriented security check.

Look for:

- authentication gaps
- authorization gaps
- exposed endpoints
- secrets in code or configuration
- sensitive data in logs
- insecure defaults
- insufficient validation
- privilege escalation opportunities
- excessive permissions
- personal or client data handling
- unsafe external integrations

Do not claim that this replaces a dedicated security review.

## 8. Database and data safety

Check:

- schema compatibility
- destructive migrations
- data loss risk
- backfills
- large-table operations
- locking
- new constraints
- indexes
- migration duration
- old/new version compatibility
- rollback behaviour
- data consistency

Identify migrations that could block production traffic.

## 9. External dependencies

For every external service identify:

- what happens if it is unavailable
- timeout behaviour
- retry behaviour
- rate limits
- authentication requirements
- API/version compatibility
- malformed response handling
- degraded-mode behaviour

Do not assume external services are always available.

## 10. Operational readiness

Check:

- deployment instructions
- rollback instructions
- runbooks
- ownership
- support contacts
- dashboards
- alerts
- incident procedures
- common troubleshooting steps
- feature-flag instructions
- manual recovery procedures

Ask:

> Could another engineer operate this feature during an incident without the original developer?

## 11. Testing evidence

Review available evidence for:

- unit tests
- integration tests
- end-to-end tests
- regression tests
- failure-path tests
- migration tests
- load or performance tests
- security tests
- production-like environment testing

Do not treat test existence as proof of correctness.

Explain what important production behaviour remains untested.

## Final output

Produce the review in the following structure.

### Production Readiness Summary

#### Decision

Choose exactly one:

- READY
- READY WITH CONDITIONS
- NOT READY
- INSUFFICIENT INFORMATION

#### Release blockers

List only issues that should prevent the release.

#### High-risk findings

| Severity | Area | Finding | Failure scenario | Recommendation |
| -------- | ---- | ------- | ---------------- | -------------- |

#### Unknowns requiring verification

List information that could materially change the decision.

#### Deployment checklist

Provide concrete actions that should happen before deployment.

#### Rollback checklist

Provide the minimum rollback procedure.

#### Post-deployment verification

State what should be checked immediately after release, such as:

- error rate
- latency
- application health
- queue depth
- database load
- failed jobs
- external API failures
- critical business metrics

## Review behaviour

Be skeptical.

Do not approve something because it appears well designed.

Do not invent evidence.

Separate confirmed problems from possible risks.

Prioritize production-impacting findings over stylistic issues.

Prefer specific failure scenarios over generic recommendations.

Ask for missing information when it materially affects the production-readiness decision.

Do not rewrite the implementation unless explicitly requested.

The engineer remains responsible for the final release decision.
