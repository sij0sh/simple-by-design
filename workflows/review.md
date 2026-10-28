# Review

Read `standards/contract.md` and the repository's adopted standards. Use checks
selected in preflight; review the complete diff and relevant surrounding code.

## Questions

- **Ownership:** Can the next maintainer locate the behavior and its state? Are
  changed owners and consumers necessary to the task?
- **Contracts:** Are dependencies acyclic and cross-owner accesses public? Does
  an approved architectural exception actually cover this change?
- **Behavior:** Are inputs, mutation, failures, side effects, resource lifetimes,
  and concurrent work traceable? Are trust-boundary guarantees established?
- **Concepts:** Do abstractions clarify a shared concept or useful boundary? Can
  callers understand them without learning unrelated features?
- **Tests:** Are changed outcomes/invariants covered at a focused boundary,
  including relevant failure paths? Do consumer tests use declared APIs?
- **Legacy:** Are findings unchanged from the bounded baseline or newly introduced?
  Did cleanup stay within scope? Were suppressions/baselines weakened?
- **Standards:** Are adopted choices followed? Are consequential deviations and
  temporary-exception revisit conditions recorded without duplicating config?

Size, nesting, duplication, and change surface are heuristics, not hard limits.
Investigate them; record a defect only when its consequence is concrete.

## Verification

Run selected commands and review-only checks. Run `scripts/verify.sh` relative to
this skill with the target repository as working directory; `--strict` fails on
missing tools or undetected verification. A repository entrypoint is authoritative:
it replaces profile fallbacks, so confirm its coverage rather than assuming it.

Classify each required check as passed, introduced failure, reproduced baseline
failure, unavailable, or not run. Non-strict skips and exit zero alone are not
proof. Compare baseline findings by identity/scope, not only counts. Do not bless
new failures by changing the baseline. Re-run affected checks after fixes.

## Findings

Give location, consequence, and action:

- **Blocker:** new/unapproved requirement violation, correctness/safety defect,
  introduced type/test/static-check failure, or uncertainty preventing confidence
  in correctness. Must resolve before claiming completion.
- **Fix now:** in-scope correction required for the agreed change. If fixing it
  would materially expand scope, agree the scope first.
- **Note:** non-blocking follow-up or reproduced legacy finding outside scope.

Architectural exceptions must be explicitly approved and applicable. Existing
baseline failures are not automatically blockers, but a legacy defect preventing
safe implementation or trustworthy verification still needs a decision. A
reported limitation is never a passing check.

## Completion

- Account for every affected owner, public contract, consumer, and dependency.
- Resolve blockers and in-scope corrections; no new unapproved violations.
- Verify changed behavior and required static checks, distinguishing baseline
  debt from regressions. State missing coverage and its implications.
- Record consequential deviations and approved exceptions; preserve baseline scope.
- Report commands/results and unrun checks. If evidence is incomplete, state what
  remains unverified instead of describing the change as fully verified.

For skill evaluation, use `evals/tasks.md` and `evals/rubric.md`: completed growth
and legacy changes provide evidence; scaffolding or approval stops do not.
