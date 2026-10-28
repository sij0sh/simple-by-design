---
name: simple-by-design
description: Use for code changes, bug fixes, refactors, implementation design, and code review; establish standards when starting or adopting a project.
---

# Simple by Design

Optimize for local reasoning: predictable change scope, explicit behavior, clear
ownership, and focused verification from greenfield through legacy adoption.

## Routing

| Task | Read |
|---|---|
| Establish standards or edit code | `workflows/preflight.md`, `standards/contract.md` |
| Language-specific work | Relevant `languages/<language>.md` only |
| Unclear ownership or design tradeoffs | `standards/local-reasoning.md` |
| Review or finish a change | `workflows/review.md`, `standards/contract.md` |
| Configure boundary checks | Relevant `templates/boundaries/` file |

## Execution

- Find adopted repository decisions; if absent, select defaults and obtain upfront
  approval under preflight. Record consequential choices once, not each task.
- Apply requirements, selected defaults, and review heuristics at their stated
  strength. Existing conventions and examples do not silently override adoption.
- Follow approval gates; an already approved plan need not be approved again.
- After editing, review the diff and run `scripts/verify.sh` with the target repo
  as working directory. Resolve the script relative to this skill's directory.
- Report new versus baselined failures, skipped checks, and missing profiles.
