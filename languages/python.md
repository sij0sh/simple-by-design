# Python profile

Top rule: Make dependencies and contracts explicit.

## 1 Structure

- Use `pyproject.toml` and a `src/` layout for packages.
- Keep code in `src/modules/<capability>/{api,domain,persistence}`.
- A module's `__init__.py` is its public entry. Keep internals private.
- Tests stay beside the feature or under `tests/`.
- Keep domain code free of framework imports.

## 2 Preferred

- Type public APIs, business logic, and integration boundaries.
- Use dataclasses for value objects.
- Pass collaborators as arguments or constructor parameters.
- Use small `Protocol` types at boundaries where substitution is real.
- Prefer plain functions and modules over class hierarchies.
- Keep import time cheap and side-effect free.

## 3 Disallowed

- Import-time I/O or mutable initialization: exception only in an explicit
  entry-point bootstrap module.
- Mutable module globals: exception only for a documented process-wide cache
  with a reset for tests.
- Metaclasses and behavior-hiding decorators: exception only for an existing
  framework integration that cannot be isolated.
- Pervasive `Any`: exception only at an untyped third-party edge, then narrow.
- Domain imports of web, ORM, or queue frameworks: exception none.

## 4 Canonical

Use comparable repository code first. Fallback:
`examples/reference-feature/python/`.

## 5 Verification

```verify
ruff check .
pyright
lint-imports
pytest -q
```

Boundaries: `templates/boundaries/.importlinter`
Brownfield ratchet: import-linter `ignore_imports`
