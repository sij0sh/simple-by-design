# JavaScript profile

Top rule: Validate runtime boundaries and keep module APIs explicit.

## 1 Structure

- Keep code in `src/modules/<capability>/{api,domain,persistence}`.
- A module entry (`index.js`) is its public API. Keep internals unexported.
- Tests stay beside the feature or under `tests/`.
- Keep domain code free of HTTP, database, and queue clients.

## 2 Preferred

- Document public functions and boundary data with JSDoc.
- Validate untrusted data with a runtime schema at the boundary.
- Model states with tagged plain objects or discriminated unions.
- Use named exports and explicit return shapes.
- Prefer composition, plain functions, and injected collaborators.
- Update data immutably at module boundaries.
- Follow the repository module format (ESM or CommonJS).

## 3 Disallowed

- Implicit globals and undeclared variables: exception none.
- `var`: exception only in legacy code that cannot be migrated.
- `eval` or `new Function`: exception none.
- Mutating built-in prototypes: exception none.
- Module-level mutable state: exception only for a documented process-wide
  cache with a reset for tests.
- Unvalidated JSON, config, or user input: exception none.
- Deep prototype hierarchies: exception only for an existing framework
  integration that cannot be isolated.
- Barrel files that re-export internals: exception only for a package root
  entry.

## 4 Canonical

Use comparable repository code first. No bundled JavaScript example.

## 5 Verification

```verify
npx --no-install eslint .
npx --no-install depcruise src
npx --no-install vitest run
```

Boundaries: `templates/boundaries/.dependency-cruiser.cjs`
Brownfield ratchet: depcruise `--ignore-known`
