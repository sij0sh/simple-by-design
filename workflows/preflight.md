# Preflight

Before editing, read `standards/contract.md` and relevant language profiles.
Read `standards/local-reasoning.md` if ownership or boundaries are unclear.

## Adopt once

Find the repository's standards record and tool configuration. If absent, propose
an initial selection appropriate to the project before implementation. For a
small script, keep this proportionally small; no architecture scaffolding.

The agent selects defaults; the user approves consequential choices together:

- Project shape, relevant profiles, supported toolchains, and runtime/dialect.
- Capability owners, dependency direction, and how public contracts are declared.
- Language-specific types/errors, resources/concurrency, and boundary validation.
- Verification entrypoint, required checks, coverage gaps, and legacy baseline.
- Justified deviations, scoped architectural exceptions, and migration limits.

Use suitable existing conventions as evidence, not automatic authority. Use
supported stable toolchains for greenfield work; profiles supply fallbacks, not
mandatory libraries/frameworks. Formatting and enforceable details belong in tool
configuration. Named tools may be replaced by equivalent repository checks.

Persist approved decisions in a short repository-owned record at its established
location (otherwise `.agents/artifacts/coding-standards.md`). Link it from existing
agent instructions; if none exist, propose a minimal pointer. Do not duplicate
configuration or restate the whole skill. Include rationale for consequential
choices and revisit conditions for temporary exceptions. Example implementations
are evidence, not standards records for unrelated projects.

Once adopted, do not reopen selections on every task. Approval already covering
a change satisfies its gate; ask again only when scope or decisions change.

## Select the change

1. Identify the owner and closest comparable implementation. Use bundled examples
   only when relevant and no suitable repository example exists.
2. Identify affected contracts, consumers, state, and dependencies. Resolve unclear
   ownership before editing; missing profiles mean universal rules plus a reported
   language-guidance gap, not invented coverage.
3. Justify new abstractions by a shared concept or useful boundary. Choose physical
   structure only when the project needs it.
4. Select verification from the adopted entrypoint/configuration or profile
   fallbacks. State which requirements need manual review. The verifier runs an
   entrypoint, not an audit of its coverage; inspect what it actually checks.
5. For legacy adoption, capture existing findings before editing with stable
   identities and bounded scope. Record commands/environment and distinguish new
   findings from existing ones. Counts alone cannot establish no regressions.
   Do not update baselines merely to absorb new violations.

Preserve behavior and public contracts unless the task changes them. Improve
legacy code only within scope; propose broader migrations separately. Never hide
new correctness/safety defects behind a baseline. When a baseline cannot be
reproduced, report uncertainty rather than claiming no new violations.

## Approval gates

Stop for changes not already approved by the task/adopted plan:

- New ownership/module/package boundaries or cross-module dependencies.
- Changed public contracts, new public interfaces, or architectural layers.
- New external dependencies or consequential changes to adopted standards.
- Architectural exceptions or baseline expansion requiring a migration decision.

A new directory, private helper, or edit to a public-entry file alone is not a
gate. Assess the architectural change. Routine compliant changes proceed.

For a gate, present: owner, concrete need, smallest change, affected contracts and
consumers, verification, exceptions, and migration scope. Wait for approval.
