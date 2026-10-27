# TypeScript profile

Top rule: Preserve type safety at runtime boundaries.

## 1 Structure

- Keep code in `src/modules/<capability>/{api,domain,persistence}`.
- Feature modules own their types. `shared/` holds infrastructure only.
- Export through a module entry (`index.ts`). Keep internals unexported.
- Tests stay beside the feature or under `tests/`.

## 2 Preferred

- Enable `strict` and `noUncheckedIndexedAccess`.
- Model states with discriminated unions.
- Validate untrusted data with a runtime schema at the boundary.
- Give important public functions explicit return types.
- Prefer small, feature-owned interfaces over global type files.
- Use composition and plain functions before classes.

## 3 Disallowed

- `any`: exception only at a checked boundary, then narrow to a real type.
- `as`: exception only after a runtime check that justifies the cast.
- `@ts-ignore`: exception only with a linked issue and the narrowest scope.
- Deep conditional or recursive generic frameworks: exception only for a
  published library API that proves the need.
- Global type directories: exception only for generated types from one source.
- Unvalidated JSON, config, or user input: exception none.

## 4 Canonical

Use comparable repository code first. Fallback:
`examples/reference-feature/typescript/`.

## 5 Verification

```verify
npx --no-install tsc --noEmit
npx --no-install eslint .
npx --no-install depcruise src
npx --no-install vitest run
```

Boundaries: `templates/boundaries/.dependency-cruiser.cjs`
Brownfield ratchet: depcruise `--ignore-known`
