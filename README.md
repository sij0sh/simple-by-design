# Simple by design — adaptive

One CLI returns one focused design prompt: draft → resolve material uncertainty if needed → review → DONE. Design only; no workflow selection or ledger maintenance.

Requires Python 3.11+ and POSIX (`flock`, atomic rename); no dependencies. Load [SKILL.md](SKILL.md) through your agent. Run from the task project, not the skill directory:

```sh
S=/absolute/path/to/simple-by-design-adaptive
python3 "$S/scripts/sbd.py" --request 'Design a greeting command; report only.'
# Do the returned job; submit JSON using its printed command, for example:
python3 "$S/scripts/sbd.py" done PRINTED_TICKET <<'JSON'
{"status":"candidate","text":"Print Hello once. No framework needed. Verify one output line when authorized; not tested."}
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
- Prompt jobs are not fresh model contexts. Review is local unless actually delegated; unavailable required independence blocks.
- JSON validation checks structure/freshness, not evidence truth, request coverage or authorization. These remain agent responsibilities. Design completion does not claim implementation correctness or tests not run.

Breaking change: `new/show/record/finish`, revision/history APIs and ledger references are removed. Legacy task files remain untouched but cannot resume under this protocol. The original `simple-by-design` skill is unchanged.

## Verification

```sh
python3 -m unittest discover -s tests -v
```

Tests cover routing, persistence, concurrency, publication recovery and instruction budgets. Fixtures are not behavioral trials; improved adherence and the ≥70% procedural-token reduction target require matched real-agent comparisons before claiming success.
