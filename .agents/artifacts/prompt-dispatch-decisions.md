# Decision record: compact CLI-driven design

Implementation plan: [prompt-dispatch-plan.md](prompt-dispatch-plan.md). Canonical records: `.agents/sbd/design.json`, run 2.

## Goal

Replace mandatory prose and ledger maintenance with a small CLI-owned adaptive prompt dispatcher. Minimize agent requirements; improve adherence through focused work, subject to behavioral validation.

## Constraints

- Plan only; implementation requires later authorization.
- Target this adaptive repository; original `simple-by-design` remains unchanged.
- Latest user instruction withdraws enforced locking and harness integration. Earlier ground lock criteria no longer apply.
- Preserve design-only authority, consequential clarification, evidence honesty, simplest adequate choices and honest completion.
- Generated documents under `.agents/artifacts/`. Local review only; no independent subagent available.

## Criteria

- `SKILL.md` ≤100 body words; no required references. ≥95% entry reduction from 2,127 required words.
- One start/resume entry; one prompt and exact return command per response. Ordinary path: start, draft submission, review submission/DONE.
- Ordinary cumulative static instructions ≤400 words, counting entry and emitted prompts. Request/candidate/source content measured separately, never silently truncated.
- Replaceable checkpoint; no ledger, graph or agent-managed revisions.
- Separate draft/resolve/review objectives; optional uncertainty resolution; no invented questions. Blocked/incomplete never DONE.
- Migration and tests measure both procedural overhead and consequential quality.

## Decisions

### D9 — How should one CLI entry drive focused prompts?

**Answer:** `sbd.py --request TEXT` starts; bare invocation resumes. Each output supplies one prompt and a `done TICKET` command. Code routes draft → optional resolve-one-need → fresh draft/review; review pass publishes and returns DONE. Validation, checkpoint and continuation share one call. No catalog, YAML or generic scheduler. Target is the adaptive skill, not the original workflow tool conducting this run.

**Rationale:** User requests code-driven navigation and focused prompts instead of ledger-maintaining agent work. Current CLI exposes `new/show/record/finish` and the trivial example needs five calls.

**Alternatives:** Merely shorten entry—retains ledger ceremony. Copy original runner—restores unnecessary workflow machinery.

**Tradeoff:** Three small jobs require minimal routing. Separate outputs are not automatically fresh model contexts; delegation is optional and must be honestly reported.

**Revisit:** A prompt job adds cost without changing consequential behavior, or needed continuation is missing.

**Supersedes:** D3.

### D10 — What checkpoint/completion contract replaces the ledger?

**Answer:** One atomic current snapshot preserves original request/authority, candidate, concise material basis/need, latest feedback, status and active ticket. No event history, evidence registry, question graph or record IDs. CLI-generated tickets reject stale/concurrent submissions. Full redraft/review against the original request replaces dependency maintenance. Only current-candidate review pass and successful idempotent publication produce DONE. Blocked prompts resume with their question. Fresh explicit requests start later runs; preserve final artifacts and leave legacy ledger state untouched.

**Rationale:** Interruption safety needs current context, not an immutable reasoning history. Existing `state.py` supplies reusable safe-path, writer-lock and atomic-write techniques. Internal persistence locks are not agent write locks.

**Alternatives:** Hidden ledger—retains unnecessary schema concepts. Transient prompts—lose reliable resume.

**Tradeoff:** Lose machine-readable reasoning history and automatic transitive invalidation; recheck the candidate against the original request. Local review is not independent. Required unavailable independent review blocks.

**Revisit:** Material basis lost on resume, stale completion, or an actual audit requirement demanding history.

**Supersedes:** D4, D5, D7, D8.

### D11 — Which prose stays or disappears?

**Answer:** Entry contains only run/return/stop instructions. Put brief scope, uncertainty and evidence reminders in the prompt that needs them. Remove witness taxonomy, provenance/policy enums, exhaustive minor-choice justification and mandatory independent-review setup. Do not move the old references wholesale into templates. Keep original request/candidate intact.

**Rationale:** User explicitly prioritizes fewer requirements and less prose. Measured mandatory entry: 575 + 397 + 1,155 = 2,127 words. Prior guardrail review identifies five consequential safeguards worth preserving without formal ceremony.

**Alternatives:** Emit a mega-prompt—same burden elsewhere. Remove all safeguards—risks overreach, invented intent and unsupported success.

**Tradeoff:** Outcome-focused reminders replace formal proof machinery; word reduction does not establish behavioral equivalence.

**Revisit:** Matched trials show consequential regressions or reading burden remains high.

### D12 — What remains of the lock?

**Answer:** No enforced write lock, extension, interception, sandbox or permissions integration. At most one advisory footer: return results through the printed command; design only. Never advertise this as write protection. Earlier ground lock requirements are explicitly withdrawn.

**Rationale:** Latest user instruction drops enforcement in favor of fewer obligations.

**Alternatives:** Harness/sandbox enforcement—withdrawn and adds setup/failure handling. Marker advertised as lock—misrepresents capability.

**Tradeoff:** No technical prevention of off-CLI writes; task authority remains a behavioral expectation.

**Revisit:** User explicitly requests technical write prevention again.

### D13 — How should migration/validation demonstrate lower overhead?

**Answer:** Build router/prompts, snapshot persistence, CLI; trim entry/docs; remove ledger-only code/tests. Preserve original skill and old state files; document the API break instead of supporting two runtimes indefinitely. Test routing, current-prompt exposure, three-call ordinary path, stale tickets, blocked resume, corruption, concurrency and crash-safe publication. Compare same-model tasks for trivial design, consequential intent, reversible choice, report-only scope, unsupported facts, material correction and blocked resumption. Measure overhead and quality separately. Target ≥70% median procedural-token reduction with no observed consequential regressions on that suite.

**Rationale:** Current tests enforce ledger mechanics, not agent adherence. Prior guardrail review offers recommendations, not measured improvement.

**Alternatives:** Word counts/schema tests only—cannot establish adherence. Permanent dual runtimes—increases concepts and maintenance.

**Tradeoff:** Small matched trials provide bounded evidence, not universal assurance. Migration intentionally drops the old runtime API.

**Revisit:** Quality regression, inadequate overhead reduction or necessary compatibility user.

**Supersedes:** D6.

## Assumptions

- Current checkpoint plus original request suffices for reliable resumption; inferred, to be tested.
- Short focused prompts improve adherence/cost; intended outcome, not an observed result.
- Numeric budgets are proposed acceptance targets, not performance measurements.

All five decisions have a documented/observed basis for adoption; these effectiveness claims remain unverified.

## Open

None unresolved within planning scope. Implementation adequacy, runtime tests and agent trials remain future verification, not completed work.

## Current view and review

D1/D2 semantic boundaries and design-only authority retained. D9–D13 replace D3–D8. Ledger mechanics are not retained through old decisions.

Challenge complete, local-only (`independent: false`); no surviving unsettled witness found in this review. No redesigned runtime, redesign tests or behavioral trials executed. No write protection or empirical adherence improvement claimed.

Stop for review. Do not implement without approval. Include `.agents/sbd/design.json` when committing this design record; bump version by 0.0.1 if a commit is requested.
