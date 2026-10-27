---
name: simple-by-design
description: Plan, implement, and verify code changes with minimal architectural complexity. Use before adding modules, abstractions, dependencies, or cross-boundary imports, and when reviewing a diff or refactor.
---

# Simple by Design

Simple by Design is the process. Local Reasoning is the philosophy. SimpleGuard
is enforcement, planned for 0.2.0.

## Non-negotiables

- Optimize for local reasoning: understand, change, and test one capability
  without knowing the whole system.
- Simple means cheap to understand and change, not short.
- Every rule must be objective, automatable where practical, and justifiable.
- No arbitrary line, class, or function limits.

## Routing

Load only the files a run needs.

| Question | Read |
|---|---|
| Architecture or ownership | `standards/local-reasoning.md`, `standards/contract.md` |
| Language patterns | `languages/<language>.md` |
| Any code change | `workflows/preflight.md` |
| After a change | `workflows/review.md` |

## Loop

1. Understand: read the owning module and a comparable implementation.
2. Plan: name the smallest change, files, boundaries, dependencies, and tests.
3. Architecture gate: apply the preflight triggers.
4. Implement: stay inside the owning module.
5. Verify: run the commands selected in preflight.

## Gate rule

Run the preflight checks for every change. If a gate trigger hits, emit the
plan and wait for approval. Otherwise proceed without a planning stop.

## Verify

Run `scripts/verify.sh` from the target repo. Add `--strict` when a missing
tool should fail. Report skipped checks and any command you did not run.

## Missing profile

If `languages/<language>.md` does not exist, apply `standards/` only and state
that in the report. Profiles for c, cpp, csharp, javascript, rust, and sql
arrive in 0.1.1.

## Templates

Start from `templates/boundaries/` for static boundary checks. Copy
`templates/AGENTS.md` into a target repo and fill the module and verify
placeholders.
