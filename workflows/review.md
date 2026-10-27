# Review

Run after implementation. Read `standards/contract.md` for the governing rules. Use the verification commands selected during preflight.

## Procedure

1. Inspect the complete diff and relevant surrounding code.
2. Compare the change with the contract and the owning module's existing patterns.
3. Check the review questions below, especially any architectural review prompts.
4. Run the selected verification commands. Use `scripts/verify.sh` when available; add `--strict` when missing tools should cause failure.
5. Classify findings and fix blockers and in-scope corrections.
6. Re-run affected verification after fixes. Report remaining notes and skipped checks.

If the verification entry point or required tools are unavailable, inspect the repository configuration where practical and report the gap. Do not describe an unrun check as passing.

## Diff questions

- **Change surface:** Are the affected files and modules necessary for this feature? Is ownership clear?
- **New concepts:** Are new interfaces, layers, packages, or dependencies justified by a concrete need?
- **Boundaries:** Do dependencies follow module contracts? Has any module's internals or owned state been accessed directly?
- **Duplication:** Has a business rule or calculation acquired more than one authoritative implementation?
- **Deletion:** Were obsolete paths or needless machinery removed where appropriate? Do not optimize for a deletion count.
- **Tests:** Do tests cover changed behavior and invariants without unnecessary dependence on implementation details?
- **Verification:** Did required tests and static checks pass? Which checks were skipped or unavailable?

Use change size and concept count as diagnostic signals, not fixed thresholds.

## Completion criteria

- All blockers and required in-scope fixes are resolved.
- Relevant tests and required static checks pass, or any unavailable checks and their implications are explicitly reported.
- No new architecture violations remain.
- New dependencies, public APIs, and abstraction layers have a concrete justification.
- Deviations from the contract are documented.
- Skipped checks and commands not run are reported.

A reported limitation is not the same as a passing check. If an unresolved issue prevents confidence in correctness, do not report the change as fully verified.

## Findings

Each finding should identify the affected location, explain the consequence, and state the required action.

- **Blocker:** Must be fixed before completion. Includes hard-fail violations and other issues that prevent a correct, contract-compliant change.
- **Fix now:** A small, in-scope correction required before completion. If the correction would materially expand scope, explain the issue and agree on the scope before proceeding.
- **Note:** A non-blocking follow-up that does not prevent completion of this change.

## Hard fail versus review prompt

**Hard fail — blocks completion**

- Module dependency cycles.
- Cross-module boundary violations.
- Type errors.
- Failing required tests or static checks.

**Review prompt — investigate and justify**

- New public interfaces.
- New dependencies.
- New abstraction layers.
- A growing change surface.
- Duplicated domain logic.

A review prompt is not automatically a defect. If investigation shows the change is unjustified or violates the contract, record the resulting finding at the appropriate severity. Otherwise, retain the rationale where needed.
