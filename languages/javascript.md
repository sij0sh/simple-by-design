# JavaScript profile

Top rule: Check maintained code statically and validate runtime boundaries.

## 1 Structure

- Default: group behavior and data by capability, without a mandatory folder tree.
- Default: expose named module APIs; keep implementation exports private.
- Default: use ESM for greenfield code; migrate CommonJS only within scope.

## 2 Preferred

- Default: use checked JSDoc with TypeScript `checkJs` for maintained code.
- Requirement: validate untrusted JSON, configuration, and user input at ingress.
- Default: model states and ordinary business outcomes as tagged objects.
- Default: reserve exceptions for operational failures; translate at adapters.
- Default: use plain functions, explicit return shapes, and injected collaborators.
- Default: use synchronous logic first; promises for asynchronous I/O.
- Requirement: own async work, await completion, propagate cancellation,
  and observe failures, including during shutdown.

## 3 Disallowed

- Requirement: no implicit globals or unchecked boundary data.
- Default: avoid `eval`, prototype mutation, and behavior-hiding inheritance.
- Default: avoid mutable module state; make state ownership explicit.
- Requirement: do not silence maintained-code type errors with blanket exclusions.

## 4 Canonical

Use repository code only when compliant with the adopted contract.
No bundled JavaScript example; module format is not an architecture template.

## 5 Verification

Requirement: check JSDoc types, lint, test behavior, and check import boundaries.
Default: use repository-supported stable tools; commands below are fallbacks,
not required dependencies. Mechanical checks do not prove architecture.
Configure `allowJs`, `checkJs`, and `noEmit` in the repository tsconfig.

```verify
npx --no-install tsc --noEmit --allowJs --checkJs
npx --no-install eslint .
npx --no-install depcruise src
npx --no-install vitest run
```

Boundaries: `templates/boundaries/.dependency-cruiser.cjs`
Requirement: brownfield baselines identify existing violations; reject new ones.
Use depcruise `--ignore-known` only with reviewed, bounded known-edge entries;
never blanket-skip legacy paths. Exceptions follow `standards/contract.md`.
