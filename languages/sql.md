# SQL profile

Top rule: Enforce data invariants and make table ownership explicit.

## 1 Structure

- Requirement: identify one owning capability for each table and its write API.
- Default: group migrations and queries by capability without requiring a schema
  or directory per capability; schema names alone do not enforce ownership.
- Default: keep views/functions with their owner and migrations ordered and focused.

## 2 Preferred

- Requirement: enforce applicable primary/foreign keys, uniqueness, not-null,
  and check constraints; application validation does not replace database invariants.
- Requirement: parameterize data values; allowlist identifiers that cannot be bound.
- Default: list query columns explicitly and qualify cross-schema object references.
- Requirement: use exact decimal or integer minor units for money, with defined
  currency/scale/rounding; define NULL meaning and timestamp/time-zone semantics.
- Requirement: define transaction scope, isolation, and conflict/retry semantics
  for multi-step invariants; keep external side effects out of retried transactions.
- Default: evolve deployed schemas with expand-contract migrations; stage backfills
  and compatibility windows before removing old columns or constraints.
- Requirement: plan recovery for destructive migrations; respect engine DDL semantics.
- Heuristic: add indexes for demonstrated query/constraint needs, not every column.

## 3 Disallowed

- Requirement: no cross-owner base-table writes bypassing the declared interface.
- Requirement: no implicit casts or ambiguous NULL/time semantics changing correctness.
- Default: avoid trigger-hidden business workflows and destructive one-step rollouts.

## 4 Canonical

Use repository migrations only when compliant with the adopted contract.
No bundled SQL example; match the repository engine and supported stable version.

## 5 Verification

Requirement: lint the configured dialect, validate migrations, and integration-test
constraints, transactions, and old/new application compatibility on the target engine.
Default: repository entry points supply database checks; the command below is a
lint fallback, not a required dependency or complete verification.

```verify
sqlfluff lint .
```

Lint config: `templates/boundaries/.sqlfluff`
Requirement: review ownership/grants separately; SQLFluff does not prove architecture.
Requirement: baseline existing findings by rule/location; reject new findings.
Use reviewed, bounded suppressions, never exclude entire legacy migration paths.
Test concurrent transaction conflicts when relevant; migration runners own work,
cancellation, completion, and failure reporting. Exceptions follow `standards/contract.md`.
