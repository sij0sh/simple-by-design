# SQL profile

Top rule: One owner per table and business rule; cross-capability access uses a declared interface.

## 1 Structure

- Group migrations by capability under `migrations/<capability>/`.
- Use a schema or naming convention that names the owning capability.
- Keep views, functions, and procedures with the capability they serve.
- Order migrations forward-only and keep each migration focused.
- Do not create a shared `common` schema for business logic.

## 2 Preferred

- List columns explicitly in production queries.
- Declare primary, foreign, not-null, unique, and check constraints.
- Make migrations transactional and idempotent where the tool allows.
- Give every index a purpose tied to a query or constraint.
- Document a backup or rollback plan for destructive changes.
- Keep names consistent with repository conventions.

## 3 Disallowed

- `SELECT *` in production queries: exception only for an explicit diagnostic
  query.
- Cross-capability writes to base tables: exception none. Use the owner's
  declared interface.
- Business logic in triggers: exception only for audit with review.
- Unqualified objects across schemas: exception none.
- Destructive migrations without approval: exception none.
- Implicit casts that change comparison semantics: exception none.
- Nullable columns with ambiguous meaning: exception none.

## 4 Canonical

Use comparable repository migrations first. No bundled SQL example.

## 5 Verification

```verify
sqlfluff lint .
```

Database-dependent checks (migration validate, integration tests) belong to
the repository entry point.
Boundaries: none enforced by SQLFluff. Ownership is a review rule.
Lint config: `templates/boundaries/.sqlfluff`
Brownfield ratchet: exclude legacy paths in `.sqlfluff`
