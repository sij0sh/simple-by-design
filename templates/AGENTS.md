# Architecture policy

Optimize for local reasoning and minimal change surface.
This repo follows Simple by Design. Before a code change, read
`.agents/skills/simple-by-design/SKILL.md`.

## Before coding

Run the preflight workflow at
`.agents/skills/simple-by-design/workflows/preflight.md`. Name the owning
module. Read the language profile for the code you will touch.

## Constraints

Read `.agents/skills/simple-by-design/standards/contract.md`. Repo-specific:

- Modules: `<module-a>`, `<module-b>`.
- No cycles between modules.
- Call another module through its public API, never its internals.

## Verification

Run `<verify command>`.
Fix new violations. Report skipped checks and exceptions.

## Cross-module changes

Stop and present a plan before adding a boundary, dependency, or cross-module
import.
