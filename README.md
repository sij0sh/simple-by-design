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
| intent / fact | `need` | resolve: ask requester / observe |

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
```

Tests cover routing, persistence, concurrency, publication recovery and instruction budgets. Fixtures are not behavioral trials; improved adherence and the ≥70% procedural-token reduction target require matched real-agent comparisons before claiming success.
