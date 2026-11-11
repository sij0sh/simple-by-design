---
name: simple-by-design-adaptive
description: Design a solution by resolving consequential uncertainty.
disable-model-invocation: true
---

# Adaptive solution design

Read [semantic boundaries](references/ambiguity.md) and [ledger contract](references/ledger.md). Set `S` to this skill's absolute directory. Run its CLI from the **task project**, not from `S`:

```sh
python3 "$S/scripts/sbd.py" --help
```

Produce a justified **solution design**, not its implementation. Inspection, tests, and experiments need the request's authority; design approval alone never authorizes implementation, deployment, destructive actions, or editing a report-only target. Pause if the needed action is unauthorized.

## Choose work by consequence

Ask: **What could still make this solution consequentially wrong?**

Record a question only with a concrete pair, defeater, or failed design check that survives the semantic gate. No witness: no gap. Do not turn this instruction into a mandatory list of questions, stages, or repeated passes.

Choose the cheapest authorized operation that can change the design or establish a required check: clarify intent, observe a fact, compare viable choices, revise the candidate design, or challenge its basis. State which decision the result can change. If no question is needed, directly produce and check the design.

- Intent → requester, never an agent-selected default.
- Fact → observation; inference stays an assumption.
- Choice → first applicable policy source; reject the strongest viable rival.
- Cheap, detectable, reversible fact/choice → explicit provisional answer and revisit condition.
- Unavailable resolver → pause with what/who is needed; no irreversible progress past it.

Use [evidence policies](references/evidence.md) where relevant, not as task routing. Use [defaults](references/defaults.md) and [contracts](references/contract.md) only when higher-precedence sources leave a choice open.

## Persist the reasoning, not a process

Use one stable task ID. `new` refuses existing tasks; resume with `show`. Do not restart, hand-edit state, or copy another task's authority.

```text
new TASK                stdin: request, constraints, permissions, design criteria
show TASK               current state + revision
show TASK --at R --history   reproducible reviewer snapshot
record TASK --at R      stdin: one question/evidence/answer/design/check/etc. record
finish TASK --at R      stdin: final evaluation of snapshot R
```

All mutations after `new` require the exact revision returned by `show`. On a stale-revision error, reload and reassess; do not merely change the number on an old evaluation. Records are immutable; use new IDs. Replacing an answer or explicitly reopening a relied-on record invalidates its dependents. Revise/recheck affected designs rather than reusing invalidated checks.

## Challenge and stop honestly

Prefer a fresh independent critic reading the immutable request, constraints, permissions, evidence, decisions, questions, design, and checks. Separate discovery from answering. Critic returns only surviving witnesses, typed resolver needs, or failed checks. Goal, assumptions, alternatives, authority, justification, and omissions are optional probes—not mandatory passes.

If no independent critic is available, perform local review and record `independent: false`. If independence is required, stop blocked rather than pretending it happened.

Record surviving findings as questions before continuing. `finish` accepts a passing evaluation of **R** and appends completion at **R+1** in one locked transaction. An intervening event makes that evaluation stale. A candidate design, supported required design checks, and no unresolved question are required; an empty ledger alone is insufficient. Budgets/retry limits imply blocked/incomplete, never success.

After completion, a cited contradiction or reached revisit condition requires explicit reopening. Reopening preserves history and the original request's authority; materially different goals use a new task.

Deliver the solution, consequential decisions and their basis, provisional assumptions/revisit conditions, remaining scoped deferrals or blockers, verification plan, and assurance limits. Design-complete does not claim implementation correctness, tests not run, independent review not obtained, or universal completeness.
