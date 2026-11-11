# Simple by design — adaptive

One CLI returns one focused design prompt: draft → resolve a gap if needed → review → DONE. Design only; no workflow selection or ledger maintenance.

Loop: decide → construct a counterexample → resolve or defer → challenge again. Review (delegated to a subagent when available) must attempt three witnesses:

- **Pair**: two outcomes consistent with everything established that the requester or a criterion would treat differently.
- **Defeater**: a plausible, unrefuted condition breaking a relied-on claim, decision or criterion; incl. criteria passing while the goal fails.
- **Decision**: a consequential choice lacking alternative, tradeoff or revisit condition, or inference stated as observed.

| Surviving gap | Review status | Next |
|---|---|---|
| none | `pass` | publish |
| choice (agent settles) | `revise` naming decisions | targeted redraft |
| intent / fact | `need` | resolve within authority; ask / observe / safely assume / block |

## Decision authority

Choose in-scope engineering means without approval: request constraints/delegation → supported project decisions/conventions → applicable defaults → simplest adequate choice. Evidence of defects defeats precedent. Defaults settle means, not goals or permissions; ask only for material unresolved user-owned intent. Explicit approvals/deferrals remain binding. Design authority never authorizes implementation or external effects.

Observe missing facts when authorized. Provisional assumptions require cheap reversal, detection before material harm/commitment, and visible detection/revisit conditions. Otherwise obtain evidence or publish a visibly conditional report: summary starts `Conditional:`, names prerequisite, verifier and decisions not to act on; criteria test the gate. Requests requiring readiness block instead. DONE completes the report, not its prerequisites.

[Design guidance](references/design.md) condenses common principles, ten language profiles and one instruction-design rule. Software draft/review consult common principles and relevant language rows even for apparently settled choices; instruction-only designs consult the instruction rule; unrelated designs skip it. Printed paths are absolute and skill-relative. No automatic language selector or extra state.

## Setup

```sh
mise install   # pinned Python and ruff from mise.toml
mise run check # lint, tests and compile check
```

`mise` is optional; the runtime requirement is Python 3.11+ on POSIX.

## Usage

Requires Python 3.11+ and POSIX (`flock`, atomic rename); no dependencies. Load [SKILL.md](SKILL.md) through your agent. Run from the task project, not the skill directory:

```sh
S=/absolute/path/to/simple-by-design-adaptive
python3 "$S/scripts/sbd.py" --request 'Design a greeting command; report only.'
# Do the returned job; submit JSON using its printed command, for example:
python3 "$S/scripts/sbd.py" done PRINTED_TICKET <<'JSON'
{"status":"candidate","summary":"Print Hello once.","criteria":["Prints exactly one line: Hello."],"decisions":[]}
JSON
# Review using the next prompt and its NEW printed ticket; passing review publishes DONE.
# Interrupted? Resume with:
python3 "$S/scripts/sbd.py"
```

`--root PROJECT` pins the task project. Printed commands include absolute paths. Invalid results do not advance; resume for the current prompt/ticket. A different active request refuses replacement; after DONE, an explicit `--request` starts a new run. Blocked means obtain the answer before continuing, not success.

## Persistence and boundaries

- Current checkpoint: `.agents/sbd-adaptive/run.json`. Final design: `.agents/artifacts/solution-design-<run-id>.md`.
- Atomic writes, internal writer mutex and opaque tickets prevent competing CLI transitions. Corrupt state fails closed. Pending publication resumes idempotently; publication errors never print DONE.
- **No agent write lock**, sandbox or tool interception. Scope reminders are advisory; unrelated tools remain usable.
- Prompt jobs are not fresh model contexts. Review asks for subagent delegation; without one it proceeds locally and says so in `basis`.
- Candidates carry decisions `{id, choice, basis, alternative, tradeoff, revisit}`; resolutions accumulate across the run. Validation checks shape only.
- JSON validation checks structure/freshness, not evidence truth, request coverage or authorization. These remain agent responsibilities. Design completion does not claim implementation correctness or tests not run.

Breaking changes: `new/show/record/finish`, revision/history APIs and ledger references are removed. Checkpoint schema 2 (structured candidate/review, accumulated resolutions) refuses schema 1 checkpoints; move `run.json` aside to start fresh. Legacy task files remain untouched. The original `simple-by-design` skill is unchanged.

## Verification

```sh
python3 -m unittest discover -s tests -v
mise run test # same suite under the pinned toolchain
```

Tests cover routing, persistence, concurrency, publication recovery, policy disclosure and budgets: SKILL body ≤100 words; ordinary emitted static surface ≤400; domain-triggered guidance ≤350 (≤750 combined when fully read). Count repeated reading and calls in trials. The previous no-reference assertion now allows exactly `references/design.md`; no ledger returns.

Fixtures test protocol/content, not agent behavior. Matched baseline/new trials must measure unnecessary questions, consequential errors, scope violations, witness quality and total instruction tokens/calls. Include delegated choices, unresolved goals/permissions, unsafe unknowns, conditional readiness, settled-but-defective Java conventions, instruction-only/nonsoftware, Python, TS/SQL and unlisted-language designs. More autonomy or the ≥70% procedural-token reduction target is not established by passing fixtures or word caps.
