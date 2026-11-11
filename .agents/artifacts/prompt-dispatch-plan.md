# Plan: prompt dispatcher, not ledger

Status: proposed; implementation not started. Target: this repository's `simple-by-design-adaptive`; original `simple-by-design` unchanged. Latest user instruction removes enforced locking/harness integration. Focus: fewer agent obligations, less reading, focused subtasks.

## Outcome and budgets

- One CLI entry starts/resumes; each response supplies one task prompt and its exact return command.
- Code routes results until `DONE`; agents do not select workflows or maintain records.
- `SKILL.md`: ≤100 body words; zero required reference reads.
- Baseline: 575 entry words + 397 ambiguity + 1,155 ledger = 2,127 required words (`wc -w`). Target entry reduction ≥95%; cumulative static instructions on ordinary draft/review path ≤400 words, including entry. Task/source content measured separately.
- Normal unambiguous task: start → draft submission → review submission/DONE. No invented questions, evidence registration, or separate certification calls.
- Preserve design-only scope, consequential clarification, evidence honesty, simplest adequate choices, honest completion. Remove ceremony, not these behaviors.

## 1. Entry and interaction

Proposed entry:

```sh
python3 "$S/scripts/sbd.py" --request '<current request>'
```

Bare invocation resumes the current run. Starting with a different request while active refuses replacement and prints the resume command. No task ID or revision bookkeeping for the agent. With no current run/request, print the start usage rather than inventing a task.

Proposed `SKILL.md` body:

> Run `python3 S/scripts/sbd.py --request '<current request>'` from the task project; `S` is this skill's directory. Bare invocation resumes. Do only the returned prompt, then use its printed return command. Continue until `DONE`; if blocked, ask for what is needed. Produce a design, not implementation.

CLI output contains only:

1. Current objective and relevant request/context.
2. Prompt-specific instructions and result shape.
3. Copyable return command with an opaque ticket.

Example return command:

```sh
python3 "$S/scripts/sbd.py" done <printed-ticket> <<'JSON'
{"status":"candidate","text":"...solution and verification plan..."}
JSON
```

`done` validates, checkpoints, and prints the next prompt immediately. No separate `show`/`next` round-trip. Invalid input prints a short repair hint without advancing.

Separate CLI outputs are separate task prompts, not a single up-front instruction dump. They do not themselves create fresh model contexts. Where fresh-agent execution is already available, a prompt can be handed off unchanged; it is not required, installed, or claimed by this skill. Review is local unless genuinely delegated. If the request requires independent review and none is available, stop blocked; never call local review independent.

## 2. Small adaptive router

| Prompt | Job | Result → next |
| --- | --- | --- |
| Draft | Inspect enough to propose the simplest adequate design against the original request. Include material basis, assumptions, and verification still needed. | `candidate` + text → review; `need` + question/consequence → resolve |
| Resolve | Settle one material uncertainty: ask the user for intent, inspect for facts, compare serious choices. | `resolved` + text/basis → draft; `blocked` + question/needs → pause |
| Review | Challenge the candidate against the original request and material failure modes; distinguish analysis from tests actually run. | `pass` + brief basis → publish; `revise` + actionable feedback → draft; `need` + question/consequence → resolve |

Code owns this routing table; no YAML, workflow catalog, generic scheduler, or agent-selected next-step field. Fixed jobs, adaptive repetition. Resolve is skipped when unnecessary; retry budgets never imply success. Revising produces a fresh candidate and review rather than tracking dependency invalidation.

Each prompt has one objective. Draft does not also perform final review; review identifies needed corrections rather than silently rewriting and approving itself. Review receives the original request, full candidate, and relevant cited basis—not the entire transcript.

Put the few necessary behavioral reminders where used: scope at draft/resolve; consequential intent versus factual investigation at resolve; request coverage and evidence honesty at review. No repeated universal rule block. A blocked prompt is reissued on resume; its `done` submission can supply the acquired answer. No separate unblock protocol.

## 3. Replace ledger with current checkpoint

One authoritative `.agents/sbd-adaptive/run.json` contains only:

- Schema version, run identity, status, current prompt/ticket.
- Original request and its constraints/permissions as supplied.
- Current candidate, current material unresolved need, concise relied-on basis, latest review feedback.
- Completed artifact path when applicable.

Update this snapshot atomically. No append-only events, question/evidence IDs, provenance enums, dependency graph, immutable criteria registry, historical snapshot API, or required rationale for every minor choice. Keep material citations in the design/result text, not a second evidence database. Do not truncate the original request or candidate to meet prompt-size targets; narrow ancillary inspection context instead.

Tickets reject stale or duplicate submissions; the CLI generates them. Use existing atomic-write, safe-path and concurrency-lock techniques internally. This persistence mutex is not an agent write lock and adds no agent steps. Two writers cannot advance the same ticket. Corrupt state fails without overwriting it.

Completion: a passing review for the current candidate lets the CLI atomically publish `.agents/artifacts/solution-design-<run-id>.md`, then mark complete and print `DONE` with its path. A publication failure never reports success. If interrupted after publication, replaying the same final ticket safely finishes the same artifact without duplicate runs. Starting a new run after completion requires a fresh explicit request. Preserve final artifacts, not a reasoning history. Legacy task files remain untouched and are never auto-imported as authority.

## 4. No enforced write lock

No Pi extension, tool interception, sandbox, permissions changes, or write-blocking promise. The CLI does not gain authority over unrelated tools.

At most one short active-prompt footer: “Return results through the printed CLI command; design only.” This is advisory. State/publishing through the CLI improves consistency, not security. No lock setup, recovery, cancellation token, or new agent obligations. The user's latest simplification overrides earlier lock requirements recorded in this design run.

## 5. File-level implementation sequence

1. **Prompt/router contract:** add `scripts/engine/prompts.py` and `router.py`; keep templates beside their result shapes and routing. Test a zero-gap draft/review path first. Avoid a generic prompt framework.
2. **Checkpoint owner:** refactor `scripts/engine/state.py` around one current snapshot. Reuse path validation, atomic replacement and internal writer locking; remove event replay dependency. Test stale tickets, resume, corruption, concurrent submissions and publication recovery.
3. **CLI adapter:** replace `new/show/record/finish` with start/resume plus the printed `done` operation in `scripts/sbd.py`. Emit a focused prompt, not a JSON ledger dump. Existing ledger CLI becomes an explicit breaking change, not a permanent second mode.
4. **Trim entry/docs:** replace `SKILL.md`; update `README.md` with one example and honest boundaries. Delete `references/ledger.md`; fold needed semantic/evidence guidance into the relevant prompts. Remove redundant `ambiguity.md`, `evidence.md`, `defaults.md`, `contract.md` after checking links; optional maintainer notes are not required reading. Do not relocate all old prose into templates.
5. **Remove obsolete machinery:** delete `scripts/engine/ledger.py` and ledger-specific fixtures/tests after replacement tests cover retained behaviors. Do not retain a hidden formal-ledger subsystem. Leave old task state untouched, explain that it is not resumable under the new protocol.
6. **Validate/adopt:** deterministic tests, same-model behavior comparison, concise results under `.agents/artifacts/`. Commit/version bump only if requested; increase by 0.0.1 when committing.

## 6. Acceptance

Deterministic tests:

- Exact routing for every result; repairable invalid submissions do not advance.
- Zero-gap path uses three CLI invocations; emitted output contains only the current prompt and return contract.
- Resume retains request, candidate and blocker; no hand-built IDs/revisions required.
- Stale/duplicate ticket, concurrent writers, corrupt state, path escape and interrupted writes fail safely.
- Publication failure/crash never produces false DONE or silently loses the final design.
- Entry/static instruction budgets; no mandatory reference links or ledger API leakage.

Agent trials, current versus proposed instructions on the same tasks/model:

- Precise trivial design; no questions or ledger ceremony.
- Consequential ambiguous intent; asks instead of guessing.
- Ordinary reversible engineering choice; chooses without needless clarification.
- Report-only request; no implementation edits.
- Plausible factual claim without observation; remains conditional.
- Material correction during review/resume; revises and rechecks original requirements.
- Blocked resolver; stops honestly and resumes with the answer.

Measure instruction tokens, CLI calls, clarification count, completion rate, omitted requirements, unsupported verification and scope violations. Aim for ≥70% median reduction in procedural tokens against the current entry/ledger protocol on this small suite, without observed consequential regressions. Treat that as a release target, not an established result; revise prompts if it misses. Fixtures cannot establish real-agent adherence.

## Decision impact and limits

Supersede D3/D4/D7/D8's ledger architecture and D5's ledger-coupled completion rules. Retain their underlying interruption safety, current-candidate review and honest completion goals. D1/D2 remain semantically relevant; D6's separation of runtime tests from behavioral evidence remains relevant. These are design proposals, not implemented capabilities.

Tradeoff: lose machine-readable reasoning history and automatic transitive invalidation. Gain fewer concepts, fewer calls and smaller prompts; full redraft/review against the original request replaces ledger dependency maintenance. Plain CLI prompt separation does not erase prior model context. No independent review, write protection or measured adherence improvement is claimed. Review of this plan is local; no subagent tool available.
