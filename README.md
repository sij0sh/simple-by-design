# Simple by Design

**A portable skill that makes coding agents plan, implement, and verify changes with minimal architectural complexity.**

Agent prompts list good architecture rules. They do not force a plan, detect a
cross-module import, or run the checks that already exist in the repo. The
result is the same review comments every time: another wrapper, another
abstraction, another boundary crossed without a decision.

Simple by Design turns those rules into a versioned workflow the agent loads
when a task needs it.

- **Simple by Design** is the process.
- **Local Reasoning** is the philosophy.
- **SimpleGuard** is enforcement, planned for 0.2.0.

## What changes

| Without the skill | With the skill |
|---|---|
| An agent extracts a shared helper for two similar handlers | The preflight asks whether the abstraction has demonstrated value |
| An agent imports another module's internals | The gate stops for a boundary plan before editing |
| Rules drift between prompts and agents | Standards, profiles, and workflows are versioned in one place |
| Verification is whatever the agent remembers | `scripts/verify.sh` runs the repo entry point or the language profile checks |
| Review catches the same defects after the change | The same questions run before and after the change |

## How it fits together

```text
                    +----------------------+
   code change ---->| SKILL.md             |
                    | routing + gate rule  |
                    +----------+-----------+
                               |
           +-------------------+-------------------+
           |                   |                   |
     standards/          languages/          workflows/
     why + rules         per-language        preflight
                         patterns            review
           |                   |                   |
           +-------------------+-------------------+
                               |
                       scripts/verify.sh
                       repo entry point
                       or profile checks
```

## Install

Requires a harness that supports Agent Skills, such as Pi. The skill uses
Markdown and Bash. No runtime dependencies.

```bash
mkdir -p ~/.agents/skills
git clone git@github.com:sij0sh/simple-by-design.git ~/.agents/skills/simple-by-design
```

For a project-local install:

```bash
mkdir -p .agents/skills
git clone git@github.com:sij0sh/simple-by-design.git .agents/skills/simple-by-design
```

Pi and other Agent Skills harnesses discover both locations. Update an
existing install with `git -C ~/.agents/skills/simple-by-design pull`.

Pi package install arrives with `simple-guard` in 0.2.0.

## Quick start

From a repository with a pending change:

```bash
pi -p "/skill:simple-by-design review the current diff"
```

The agent loads `workflows/review.md` and reports blockers, fixes, and notes.
For a code change, the same skill runs `workflows/preflight.md` before editing
and `scripts/verify.sh` after.

In an interactive Pi session:

```text
/skill:simple-by-design add a read endpoint to the orders module
```

## What is inside

| Path | Purpose |
|---|---|
| `SKILL.md` | Entry point, routing table, loop, gate rule |
| `standards/local-reasoning.md` | Why the style exists, 10 standards, measures, layout |
| `standards/contract.md` | Required defaults, avoid list, 5 enforceable constraints |
| `languages/` | TypeScript, Python, Go, Java profiles with verify commands |
| `workflows/` | Preflight checks and post-change review |
| `templates/` | `AGENTS.md` policy and boundary configs |
| `scripts/verify.sh` | Entry-point resolution and profile checks |
| `examples/reference-feature/` | Small TS and Python feature in the target shape |
| `evals/` | Fixture, tasks, rubric, baseline and skill results |

Read [SKILL.md](./SKILL.md) for the routing. Read
[standards/local-reasoning.md](./standards/local-reasoning.md) for the
philosophy and [standards/contract.md](./standards/contract.md) for the rules.

## Verify

Run from the target repo:

```bash
/path/to/simple-by-design/scripts/verify.sh
```

| Flag | Effect |
|---|---|
| `--strict` | A missing tool is a failure instead of a skip |
| `--only=<language>` | Run a profile even when no stack marker is present; repeatable |

Resolution order: `SBD_VERIFY_CMD`, `make verify`, `npm run verify`,
`just verify`, then stack detection and the profile `verify` blocks. The
script never installs tools, uses the network, or changes Git state.

The bundled `examples/reference-feature/` is a working TS and Python
reference.

## Language profiles

v0.1.0 ships TypeScript, Python, Go, and Java. The remaining profiles - C, C++,
C#, JavaScript, Rust, and SQL - arrive in 0.1.1. A language without a profile
gets the universal standards only, and the agent says so in the report.

## Uninstall

```bash
rm -rf ~/.agents/skills/simple-by-design
```

For a project-local install:

```bash
rm -rf .agents/skills/simple-by-design
```

The skill writes no data outside its own directory.

## Limits

These are defaults, not proofs of simplicity. The static checks catch cycles,
cross-module imports, and type errors. Change surface, abstraction growth, and
duplicated domain logic still need human review. The skill can be ignored by an
agent; SimpleGuard and CI will add hard gates in 0.2.0.

The v0.1.0 eval used one run per task. Treat the result as directional, not
statistical. See [the results](./evals/results/v0.1.0.md) and
[the baseline](./evals/results/baseline.md).

## Troubleshooting

**The skill does not load**

Check that `~/.agents/skills/simple-by-design/SKILL.md` exists, then run
`/reload` in Pi. Use `/skill:simple-by-design` to force it.

**A verify check is skipped**

The first word of the command was not found on `PATH`. Install the tool or run
with `--strict` to turn the skip into a failure.

**A language has no profile**

Apply the standards only and note it in the report. The profile lands in 0.1.1.

## More

- [Changelog](./CHANGELOG.md)
- [Eval tasks](./evals/tasks.md)
- [Boundary templates](./templates/boundaries/)
- [Reference feature](./examples/reference-feature/)

## License

MIT. See [LICENSE](./LICENSE).
