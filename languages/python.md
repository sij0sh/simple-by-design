# Python profile

Top rule: Make function contracts and resource lifetimes explicit.

## 1 Structure

- Default: group modules by capability; no mandatory package or layer per feature.
- Default: keep module APIs small; use private names for implementation details.
- Heuristic: use a `src/` package layout when packaging/import isolation warrants it.

## 2 Preferred

- Default: type maintained functions, including business logic and boundaries.
- Default: use dataclasses for data; frozen dataclasses for value objects.
- Default: represent ordinary business outcomes as values, not exceptions.
- Default: raise specific exceptions for operational failures; preserve causes.
- Requirement: use context managers for resource acquisition and release.
- Default: use functions and concrete collaborators; Protocols for real contracts.
- Default: synchronous code first; async only for an actual concurrency need.
- Requirement: own tasks/threads, join them, provide cancellation or cooperative
  shutdown, and observe failures; use structured task groups where supported.

## 3 Disallowed

- Default: avoid import-time I/O, mutable globals, and behavior-hiding decorators.
- Requirement: narrow untyped third-party data before domain use.
- Requirement: do not swallow broad exceptions or abandon background tasks.

## 4 Canonical

Use repository code only when compliant with the adopted contract.
Fallback: `examples/reference-feature/python/`; adapt, do not copy its layout.

## 5 Verification

Requirement: type-check, lint, test behavior, and check configured import boundaries.
Default: use repository-supported stable tools; commands below are fallbacks,
not required dependencies. Mechanical checks do not prove architecture.

```verify
ruff check .
pyright
lint-imports
pytest -q
```

Boundaries: `templates/boundaries/.importlinter`
Requirement: brownfield baselines identify existing violations; reject new ones.
Use `ignore_imports` only for reviewed, bounded existing edges; track type/lint
findings by identity, not just count. Never blanket-skip legacy packages.
Exceptions follow `standards/contract.md`.
