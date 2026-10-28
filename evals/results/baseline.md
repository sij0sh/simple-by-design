# Baseline eval

Historical record: obsolete policy/config; not evidence for the current redesign
or long-term maintainability. Rerun current scenarios and checks.


Date: 2026-10-27
Condition: no skill loaded.
Fixture: `evals/fixture/` clean, except task 1 uses
`evals/fixture/seed-small-fix.sh`.
Runs: 1 per task. The planned 3 runs were cut for cost; treat results as
directional only.

Task language: 1 TS, 2 Py, 3 TS, 4 Py.

| Task | Files | New abstractions | New violations | New test failures | Pattern match | Asked on gate |
|---|---|---|---|---|---|---|
| 1 small fix | 1 | 0 | 0 | 0 | yes | n/a |
| 2 endpoint | 3 | 0 | 0 | 0 | yes | no (gate hit) |
| 3 dedup | 3 | 1 | 0 | 0 | no | no gate |
| 4 cross-boundary | 3 | 0 | 2 | 0 | no | no (gate hit) |
| **Total** | **10** | **1** | **2** | **0** | **2 of 4** | **0 of 2** |

## Notes

- Task 1: one-line `Math.floor` to `Math.round`, matching billing. All 4 tests
  pass.
- Task 2: added the endpoint, view value object, public export, and one test.
  All 5 tests pass. It edited a module public entry without asking.
- Task 3: added `src/shared/lookup.ts`, a generic lookup abstraction, and
  pointed both module APIs at it. All tests pass.
- Task 4: imported `orders.domain` internals from `billing.api`. All 6 tests
  pass, but dependency-cruiser/import-linter report 2 cross-module internal
  imports. It did not ask before crossing the boundary.
- New test failures counted against the clean start state. No run introduced
  a test failure.

## Commands

```
npm run verify                 # TS tasks
pytest -q                      # Python tasks
depcruise src                  # TS boundary check
PYTHONPATH=src lint-imports    # Py boundary check
```
