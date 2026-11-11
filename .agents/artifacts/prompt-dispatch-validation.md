# Prompt dispatcher: implementation verification

Status: implemented; deterministic checks pass. Behavioral adoption gate pending.

## Changes

- `scripts/engine/{router,prompts}.py`: fixed draft/resolve/review routing; one prompt/result contract at a time.
- `scripts/engine/state.py`: current checkpoint, opaque tickets, writer mutex, atomic writes and recoverable publication.
- `scripts/sbd.py`: `--request`, bare resume, printed `done TICKET` command; no task/revision bookkeeping.
- `SKILL.md`: 53 body words, no required references. Old ledger code, reference directory and ledger-only tests removed.
- `README.md`: usage, API break, advisory scope and evidence limits.
- Legacy task files/original skill unchanged. No enforced write lock, extension or harness integration.

## Observed checks

- Baseline before edits: `python3 -m unittest discover -s tests -v` — 48 passed. Previously reported documented-example failure not reproduced.
- Replacement suite, final run: same command — 37 passed.
- `python3 -m compileall -q scripts tests` — passed.
- `git diff --check` — passed.
- CLI ordinary path completes in three invocations: start, candidate submission, passing review submission. Resume prints DONE without starting another run.
- Tested invalid/stale/duplicate submissions, blocked resumption, full request/candidate preservation, concurrent draft and final submissions, symlinks/FIFOs/path checks, writer death/timeout, corrupt state, fault-injected replace/fsync/publication failures and replay after publication-before-completion interruption.
- Directory names are synced as well as file replacements; retries also sync previously created names.
- Commands remain executable from another working directory with spaces/apostrophes in the project path.

The baseline and replacement suites test different protocols; passing both is not evidence of unchanged agent quality.

## Word/call budgets

| Measure | Observed |
| --- | ---: |
| Entry body | 53 words; limit 100 |
| Entire entry including frontmatter | 67 words |
| Required references | 0 |
| Reduction from 2,127-word mandatory baseline, including new frontmatter | 96.85% |
| Ordinary static surface: body + draft/review outputs | 292 words; limit 400 |
| Ordinary CLI invocations | 3 |

Static count uses `/skill/scripts/sbd.py` and `/project`, counting all output except task-context JSON; actual paths/context vary. Tests count the emitted static surface, not just instruction constants. These are word counts, **not measured model-token savings**.

## Pending real-agent comparison

No independent subagent tool provided in this session; no matched behavioral trials or independent review performed. Scripted scenarios check result routing, not whether an agent chooses the correct result or tells the truth. Do not claim improved adherence, ≥70% median procedural-token reduction, or absence of consequential regressions.

Run old/new instructions on the same model and seven tasks: precise trivial design; consequential intent ambiguity; reversible engineering choice; report-only authority; unobserved factual hypothesis; material correction; blocked resolution/resumption. Include unavailable required independent review in the blocker case. Baseline instructions can be recovered from git `41b6f3eeceb73348cce108bff060e53f3c1bbbbf` without modifying the original skill.

Record procedural tokens, CLI calls, questions, completion, omitted requirements, unsupported verification and scope violations. Adoption gate: ≥70% median procedural-token reduction with no observed consequential regressions on this bounded suite. Actual power-loss/filesystem durability testing also not performed; recovery tests inject failures at the relevant boundaries.

Commit requested after verification; version bumped to 0.0.2. Narrow `.gitignore` exceptions retain the approved plan, decisions, workflow state and this verification record; other agent artifacts/state remain ignored.
