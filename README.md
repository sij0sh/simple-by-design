# Simple by Design

A coding-agent skill for choosing standards upfront so later changes stay easy to
locate, understand, and verify.

Without shared decisions, each feature can introduce another layout, abstraction,
or error convention. This skill establishes a small universal core, selects
idiomatic language defaults, and carries those decisions into existing code.

```text
Select standards -> approve once -> implement -> verify change
                                          ^            |
                                          +------------+
Legacy adoption: baseline existing debt; introduce no new violations.
```

## What changes

| Repeated design decision | Adopted default |
|---|---|
| Where does behavior belong? | Its capability owner, with explicit state and contracts |
| Should similar code become shared? | Only for a shared concept or useful boundary |
| Which folder architecture is required? | None; structure follows actual project needs |
| Must legacy code be rewritten? | No; bounded improvements without new violations |
| Does a small diff prove simplicity? | No; inspect affected owners, contracts, and behavior |

Local reasoning means understanding a capability without reconstructing unrelated
features. It applies to applications, libraries, CLIs, scripts, UI, systems, and
data work. Language profiles specialize the rules; they do not prescribe frameworks.

## Setup and first use

Requires a coding agent that discovers directory-based skills. Add this checkout
to its skill search path, or copy the whole directory to its documented skill
location. Keep `SKILL.md`, profiles, workflows, templates, and scripts together;
installation/discovery commands depend on the host.

Ask the agent:

```text
Use simple-by-design. Inspect this repository and propose coding standards
for approval before implementation. Preserve existing public contracts;
identify verification coverage and any legacy baseline.
```

The agent selects consequential defaults and records approved decisions in the
repository. Existing conventions inform selection; they do not silently override
it. Subsequent compliant changes reuse that record instead of reopening choices.
See [preflight](workflows/preflight.md) for adoption and approval gates.

## Rules at three strengths

- **Requirements:** correctness, safety, ownership, explicit acyclic dependencies,
  declared public contracts, trust-boundary validation, and behavioral verification.
- **Defaults:** concrete functions/data, capability-first organization, explicit
  control flow, narrowly owned mutation, and idiomatic language choices.
- **Heuristics:** size, nesting, duplication, and change surface prompt review;
  they are not numeric gates.

Architectural exceptions need approval, scope, and rationale. Temporary exceptions
need a revisit condition. Correctness and safety cannot be waived. Existing debt
gets a bounded baseline, not permission to add violations or skip legacy paths.

## Languages and verification

Profiles cover TypeScript, JavaScript, Python, Go, Rust, Java, C#, C, C++, and SQL.
They select types, outcomes/errors, ownership/resources, concurrency, boundaries,
and verification defaults. Missing profiles fall back to universal rules with an
explicit coverage gap.

Run from the target repository, using the actual path to this checkout:

```bash
/path/to/simple-by-design/scripts/verify.sh --strict
```

Resolution: `SBD_VERIFY_CMD`, `make verify`, `npm run verify`, `just verify`, then
detected language-profile commands. Repository entrypoints replace profile checks;
inspect their coverage. `--only=python` selects fallback profiles, not extra checks
on top of an entrypoint. `--strict` fails on missing tools or undetected checks.
Non-strict mode can skip checks; exit zero alone does not mean fully verified.

Tools enforce objective rules; ownership and design still require review. SQL
lint does not prove schema ownership. C/C++ fallback commands assume CMake;
repository entrypoints may use other build systems.

## Evidence and maintenance

[Reference implementations](examples/reference-feature/) demonstrate TypeScript
and Python contracts, consumer tests, and configured checks. Their layouts are
illustrative. Each example declares coverage and limitations in `architecture.json`.

[Evaluation tasks](evals/tasks.md) exercise greenfield implementation, second-feature
variation, boundary changes, and bounded legacy work. Historical results predate
this policy; they do not establish its long-term maintainability benefits.

From this checkout, check profile consistency and verifier behavior:

```bash
bash scripts/check-profiles.sh
python3 -m unittest discover -s scripts -p 'test_*.py'
```

## Removal

Remove the skill search-path entry or copied skill directory from your agent.
Repository standards records, configuration, and code remain; remove their links
or revise those decisions separately if no longer wanted.

## Reference

- [Agent entrypoint](SKILL.md)
- [Authoritative contract](standards/contract.md) and [rationale](standards/local-reasoning.md)
- [Language profiles](languages/)
- [Review and completion](workflows/review.md)
- [Boundary templates](templates/boundaries/)
- [MIT license](LICENSE)
