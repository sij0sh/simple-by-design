---
name: simple-by-design
description: Must use for any code change, bug fix, refactor, code review, or implementation design.
---

# Simple by Design

Optimize for local reasoning: minimize the unrelated context needed to understand, change, and test a capability.

## Routing

| Task | Read |
|---|---|
| Before any code edit | `workflows/preflight.md`, `standards/contract.md` |
| Language-specific work | `languages/<language>.md` if present |
| Unclear ownership or boundaries | `standards/local-reasoning.md` |
| Diff review or after editing | `workflows/review.md`, `standards/contract.md` |
| Configure boundary checks | Relevant file in `templates/boundaries/` |

## Execution

- Follow preflight. If an approval gate triggers, present the plan and wait; otherwise implement.
- After editing, review the diff and run `scripts/verify.sh` with the target repo as the working directory. Resolve the script relative to this skill's directory.
- Report failed or skipped checks and missing language profiles.
