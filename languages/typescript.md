# TypeScript profile

Top rule: Preserve type safety at runtime boundaries.

## 1 Structure

- Default: group types and behavior by capability; no prescribed folder tree.
- Default: expose a small module entry; keep implementation exports private.
- Heuristic: split packages only for an actual dependency or deployment boundary.

## 2 Preferred

- Default: enable `strict`, `noUncheckedIndexedAccess`, and `exactOptionalPropertyTypes`.
- Requirement: accept untrusted input as `unknown`; validate before domain use.
- Default: use discriminated unions for states and ordinary business outcomes.
- Default: reserve exceptions for operational failures; translate at adapters.
- Default: use plain functions, immutable values, and explicit public return types.
- Heuristic: introduce interfaces only for real consumer contracts.
- Default: synchronous logic first; use promises for asynchronous I/O.
- Requirement: own async work, await completion, propagate cancellation,
  and observe failures, including during shutdown.

## 3 Disallowed

- Requirement: no unchecked `any`, assertions, or suppression at ingress.
- Default: avoid recursive generic frameworks and global type dumping grounds.
- Requirement: keep runtime validation even when static types appear sufficient.

## 4 Canonical

Use repository code only when compliant with the adopted contract.
Fallback: `examples/reference-feature/typescript/`; adapt, do not copy its layout.

## 5 Verification

Requirement: type-check, lint, test behavior, and check configured import boundaries.
Default: use repository-supported stable tools; commands below are fallbacks,
not required dependencies. Mechanical checks do not prove architecture.

```verify
npx --no-install tsc --noEmit
npx --no-install eslint .
npx --no-install depcruise src
npx --no-install vitest run
```

Boundaries: `templates/boundaries/.dependency-cruiser.cjs`
Requirement: brownfield baselines identify existing violations; reject new ones.
Use depcruise `--ignore-known` only with reviewed, bounded known-edge entries;
never blanket-skip legacy paths. Exceptions follow `standards/contract.md`.
