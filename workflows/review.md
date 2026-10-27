# Review

Run after changes. Read `standards/contract.md` for the rules behind these
questions.

## Diff questions

- Change surface: how many modules and files changed?
- New concepts: how many interfaces, layers, packages, or dependencies?
- Boundaries: were module roots or internals crossed without a contract?
- Duplication: is a business rule now implemented in more than one place?
- Deletion: what was removed versus added?
- Tests: do they assert behavior and invariants, not internals?

## Completion criteria

- Relevant tests and static checks pass.
- No new architecture violations.
- No unneeded dependencies or public APIs.
- Deviations are documented.
- Skipped checks are reported.

## Findings

- Blocker: must be fixed before completion.
- Fix now: small, local correction in this change.
- Note: follow-up with no effect on this change.

## Hard fail versus review prompt

Hard fail: module cycles, cross-module boundary violations, type errors.

Review prompt: new public interface, new dependency, new abstraction layer,
growing change surface, duplicated domain logic.
