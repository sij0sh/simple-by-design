# Eval rubric

Score pass/fail/unknown from completed diff, tests and decisions; cite evidence.
Unknown verification is not a pass. Approval-only responses are incomplete.

| Requirement | Passing evidence |
|---|---|
| Local reasoning | Owner, behavior and affected contracts identifiable; reviewer can explain change without tracing unrelated owners |
| Contract | Consumers use declared public symbols/paths/directories; no mandatory barrel; contract inputs/outputs usable publicly |
| Dependencies/state | Acyclic owner graph; each state item has one owner; no new internal reach-through or shared mutable ownership |
| Behavior | Scenario acceptance and failure cases tested; existing contract behavior preserved unless approved |
| Scoped change | Unrelated owners untouched; necessary adjacent edits explained; legacy violations not increased |
| Verification | Baseline and final selected checks recorded; introduced regressions absent; known failures matched by diagnostic, not blanket skip |
| Decisions | Repository defaults recorded once; new architectural choices approved; directory creation alone not gated |

Owner-local tests may import internals, even from a separate test directory.
Consumer tests use the declared API. Record which kind each test is.

Report unavailable tools/checks separately from failing checks. Repository verify
entrypoints are authoritative only for documented coverage; a green command does
not prove uncovered requirements. Strict verification cannot pass missing checks.

Layout, file count, duplication and abstraction count are heuristics, not scores.
Judge whether a second variation stays understandable; neither forced extraction
nor forced duplication wins. Do not infer long-term outcomes from one-shot runs.
