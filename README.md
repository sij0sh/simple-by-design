# Simple by design — adaptive

Design solutions by resolving consequential uncertainty. No workflow catalog or scheduler. Design-only; does not implement proposed solutions.

- Entry: [SKILL.md](SKILL.md)
- Runtime/API: [ledger contract](references/ledger.md), including a runnable zero-question example
- Requirements: Python 3.11+, POSIX filesystem (`flock`, atomic rename); no third-party packages
- Load the skill directory through your agent's skill support. Run its scripts from the task project.

```sh
python3 scripts/sbd.py --help
python3 -m unittest discover -s tests -v
```

State: `.agents/sbd-adaptive/`. Revision-checked, logically append-only history; atomic writes and explicit reopening. Validation checks structure/freshness, not truth, source authenticity, or tool permissions. Local tests/scenario fixtures do not prove behavioral improvement or universal completeness.
