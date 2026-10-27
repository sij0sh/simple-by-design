# Preflight

Run before editing. Read `standards/contract.md`.
Read `standards/local-reasoning.md` when ownership or boundaries are unclear.

## Checks

1. Identify the module that owns the behavior.
2. Inspect the closest comparable implementation. Use
   `examples/reference-feature/` only when relevant and no
   repository example exists.
3. Load each relevant `languages/<language>.md` profile.
4. Justify any new architectural abstraction by its concrete need.
5. Identify affected modules, public APIs, and dependencies.
6. Select verification commands from the repository entry point,
   or the language profile. If neither exists, inspect project
   configuration and report verification gaps.

Resolve unclear ownership before editing. If a language profile
is missing, apply the universal standards and report the gap.

## Approval gates

Stop before editing and request approval for:

- A new module or package boundary.
- A change to a public API contract.
- A new external dependency.
- A new cross-module dependency or boundary crossing.
- A new architectural abstraction layer or public interface.

A new directory or an edit to a public-entry file alone is not
a gate. Assess the architectural change, not just the file path.

If no gate triggers, continue without presenting a plan.
If a gate triggers, do not edit until the user approves.

## Plan

- Trigger and rationale:
- Owning module:
- Existing pattern:
- Smallest change:
- Files touched:
- Boundaries, APIs, dependencies:
- Verification commands:
- Exceptions and rationale:
