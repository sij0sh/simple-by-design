# 0003. Bounded instructions with one on-demand reference

- Status: accepted (retroactive)
- Date: 2026-11-11

## Context

`tests/test_cli.py` enforces a SKILL body of at most 100 words, an ordinary emitted static surface of at most 400 words, and a guidance reference of at most 350 words (750 combined). Commit `0b289ed` added `references/design.md` and made draft and review print its absolute path instead of embedding the guidance. `tests/test_prompts.py` checks the disclosure.

## Decision

Keep exactly one guidance file, `references/design.md`, containing common defaults, ten language profiles and the instruction rule. Draft and review append only its absolute path; resolve omits it. Budgets are enforced by tests rather than review convention.

## Consequences

- New rules must fit the word budgets or replace existing text; tests fail otherwise.
- Guidance is read on demand, so it does not inflate every prompt.
- There is no language selector or extra state; the agent chooses relevant rows.
- The skill directory must ship `references/design.md` alongside `scripts/`.
