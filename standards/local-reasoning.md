# Local Reasoning — Coding Style v1.1

This file explains why the style exists. `standards/contract.md` is authoritative for code rules. `workflows/preflight.md` owns pre-edit checks and approval gates; `workflows/review.md` owns post-change review.

Language profiles may add language-specific rules or specialize universal rules. They should not repeat rules that already apply unchanged.

## Governing idea

Optimize for local reasoning. A developer should be able to understand, change, and test a business capability without understanding the entire system.

## Principles

1. **Localize.** Related data, behavior, and decisions belong together.
2. **Expose.** Visible dependencies, state, ownership, and side effects make behavior easier to trace.
3. **Minimize.** Every additional concept costs attention; introduce one only when its benefit justifies that cost.
4. **Standardize.** Familiar patterns reduce the effort required to understand and review code.
5. **Verify.** Clear boundaries and observable behavior make correctness cheaper to check.

## Design implications

1. **Capability ownership.** Organize code around cohesive business capabilities so developers can find where behavior belongs.
2. **Predictable dependencies.** One-way dependency flow limits how far changes can propagate.
3. **Explicit behavior.** Visible control flow and dependencies reduce the need to reconstruct hidden state.
4. **Locality of change.** A feature that routinely requires unrelated modules to change may indicate unclear ownership or excessive coupling.
5. **Single source of truth.** One authoritative owner for each business rule, calculation, and piece of state prevents divergent behavior.
6. **Justified abstractions.** Interfaces, factories, base classes, and extra layers add concepts. Reuse, genuine substitution, or meaningful isolation of complexity can justify them; abstraction alone is not a benefit.
7. **Consistency.** Familiar patterns make code easier to compare and defects easier to notice.
8. **Separated concerns.** Business decisions should remain understandable without needing to understand transport, storage, or framework details.
9. **Behavior-focused tests.** Tests of observable outcomes and invariants give confidence when implementation details change.
10. **Deletion.** Removing obsolete paths and machinery reduces the number of concepts and behaviors developers must account for.

These implications explain the contract; they are not a separate approval policy or an additional checklist.

## Review lenses

Use these as qualitative signals, not quotas or numeric thresholds.

- **Change surface:** How many modules and files must change for the feature?
- **Cognitive load:** How much of the system must a developer understand to make a safe change?
- **Coupling:** How many other modules could be affected by one change?
- **Discoverability:** How quickly can a developer find the owner of a behavior?
- **Predictability:** Does the code behave as its structure and names suggest?
- **Deletion cost:** Can obsolete functionality be removed without tracing unnecessary dependencies?

A large change surface is not automatically wrong. Assess whether the affected modules have legitimate ownership and dependency relationships.

## Illustrative capability layout

```text
src/
  modules/
    <capability>/
      api/
      domain/
      persistence/
  shared/
    logging/
    database/
    config/
```

This is an example, not a required directory structure. Create folders and layers only when the code needs them.

`shared/` is for genuinely cross-cutting infrastructure, not a default home for business logic without a clear owner. A capability should own its business rules and expose a small, intentional interface where cross-capability access is needed.

## Closing

Simple means cheap to understand and change, not short.
