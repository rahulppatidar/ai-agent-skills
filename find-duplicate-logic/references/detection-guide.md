# Detection Guide

Use this reference when candidate matches are ambiguous.

## Strong semantic signals

These signals are more important than textual resemblance:

### Same predicate

```ts
age >= 18
```

and

```ts
age > 17
```

can be equivalent.

### Same normalization/transformation

```ts
email.trim().toLowerCase()
```

and a helper that performs the same normalization may represent the same rule.

### Same state transition

Two implementations that both move `pending -> approved` only after the same prerequisite may duplicate a workflow rule even if one lives in a command handler and another in a model method.

### Same calculation

Equivalent formulas, rounding rules, caps, thresholds, or ordering of operations are strong signals.

### Same validation

If two modules independently reject the same invalid state for the same domain reason, investigate duplication.

### Same external side effect conditioned on the same rule

Two paths that independently decide when to charge, email, publish, enqueue, or delete can indicate duplicate policy.

## Weak signals

These alone should not trigger a duplicate finding:

- same framework decorators;
- same HTTP status handling;
- same logging pattern;
- same try/catch structure;
- same ORM calls with different domain meaning;
- same UI component layout;
- same method name in unrelated bounded contexts;
- same generic algorithm applied to different policies.

## Candidate comparison matrix

For difficult cases, compare candidates using this matrix:

| Dimension | Target | Candidate | Equivalent? |
|---|---|---|---|
| Domain concept | | | |
| Inputs | | | |
| Preconditions | | | |
| Core predicates | | | |
| Calculation/transformation | | | |
| Output | | | |
| State mutation | | | |
| External side effects | | | |
| Error behavior | | | |
| Boundary cases | | | |
| Ownership | | | |

A candidate should normally match on the domain concept plus several behavioral dimensions before it is classified as a semantic duplicate.

## Examples

### Semantic duplicate

Target:

```ts
function canPurchase(user) {
  return user.country === 'IN' && user.age >= 18
}
```

Candidate:

```ts
const allowed = customer.age > 17 && customer.countryCode === 'IN'
```

If `customer.countryCode` and `user.country` represent the same field and both decisions govern the same purchasing rule, this is likely a semantic duplicate.

### Partial overlap

Target:

```ts
subtotal * discountRate
```

Candidate:

```ts
Math.min(subtotal * discountRate, maxDiscount)
```

The core calculation overlaps, but the maximum-discount policy is meaningful. Classify as partial overlap unless context proves the cap is irrelevant.

### Similar, not duplicate

Two route handlers both:

1. parse request;
2. validate body;
3. call service;
4. return JSON.

This is a shared technical pattern, not duplicate business logic, unless the service decisions themselves overlap.

### Intentional duplication

Frontend and backend may both enforce a maximum input length. The rule is duplicated behaviorally, but the frontend copy may exist for UX while the backend remains authoritative for security/integrity.

Report the duplication, explain the boundary, and do not automatically recommend removing either check. A shared schema may be appropriate only if the architecture already supports it.

## Search strategy examples

Suppose the target calculates a cancellation fee when:

- booking is confirmed;
- cancellation occurs within 24 hours;
- fee is 20% of price;
- fee is rounded to currency precision.

Search for:

- cancellation / cancel / refund / penalty / fee;
- confirmed status enum;
- `24`, duration helpers, deadline calculations;
- `0.2`, `20`, percentage helpers;
- price/money rounding helpers;
- tests mentioning cancellation within one day;
- writes to fee/refund/payment fields.

The combination of signals is much stronger than searching for `calculateCancellationFee`.
