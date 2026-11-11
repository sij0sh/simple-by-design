# Architecture

Status: current

`simple-by-design-adaptive` is a local CLI that routes one agent through a fixed design sequence: draft → resolve one gap → review, then publish. It is design-only; there is no ledger, agent-selected workflow or implementation step.

```mermaid
flowchart LR
  U[User request] --> C["scripts/sbd.py"]
  C --> P["engine/prompts.py"]
  C --> S["engine/state.py"]
  S --> R["engine/router.py"]
  P -. absolute path .-> G["references/design.md"]
  S --> J[".agents/decision.json"]
  S --> A[".agents/artifacts/solution-design-<ticket>.md"]
  R -. fixed phase transitions .-> T["draft / resolve / review / complete"]
```

## Components

- `scripts/sbd.py` is the CLI. It starts a run with `--request`, resumes with no arguments, and accepts one result with `done TICKET`. It prints the next prompt or resumption command; errors go to stderr with a resume hint.
- `scripts/engine/router.py` owns checkpoint schema 3, result shapes and transitions. `phase` is `draft`, `resolve`, `blocked`, `review`, `publishing` or `complete`; payload keys appear only when needed. `draft` accepts `candidate` or `need`; `resolve` accepts `resolved` or `blocked`; `review` accepts `pass`, `revise` or `need`. `advance` rotates the opaque ticket on every non-pass result and keeps the final ticket for exact publication replay; the artifact name derives from that ticket.
- `scripts/engine/state.py` is the only writer. It resolves the task root, stores `.agents/decision.json` with sibling `.decision.lock` and temporary files, serialises writers with `flock`, rejects symlinked ancestors and non-regular files, and publishes via temporary file, `fsync`, `os.replace` and directory `fsync`. Duplicate JSON keys are rejected. Old-path or non-schema-3 state fails closed without auto-import. A durable passing review is replayed idempotently; conflicting artifacts are never overwritten, and completion compacts the checkpoint to `{schema_version, phase, ticket}`.
- `scripts/engine/prompts.py` holds the static prompt text, the JSON contract and bounded context. Draft and review append an absolute path to `references/design.md`; resolve omits it. The printed return command uses absolute paths.
- `references/design.md` holds common design defaults, ten language profiles and the instruction-design rule. The agent reads it on demand; it is not embedded in every prompt.
- `tests/` holds the stdlib `unittest` suite covering routing, state, concurrency, publication recovery, prompt disclosure and instruction budgets.

## Invariants

- **Design only:** prompts and completion never authorise implementation or external effects.
- **One state owner:** the CLI owns transitions; the agent supplies only the requested result.
- **Opaque tickets:** a ticket is accepted once, only for the current prompt; stale or duplicate results do not advance. The final ticket is retained through publication for exact replay and names the artifact.
- **Fail closed:** corrupt, legacy or symlinked state is refused rather than repaired.
- **Portable runtime:** Python 3.11+ on POSIX, standard library only.
- **Bounded instructions:** SKILL body ≤100 words; ordinary emitted static surface ≤400 words; guidance ≤350 words; combined ≤750 words.
- **No ledger:** one current snapshot, no history, workflow selection or agent-authored next step. Completed state is a compact pointer; the Markdown artifact is the durable record.

## Data flow

A request enters `sbd.py` and becomes a checkpoint. The agent performs the printed prompt, submits JSON through the printed ticket, and receives the next prompt. A `need` result temporarily routes to `resolve`; `revise` returns to `draft` with named gaps; `blocked` pauses until resumed. A passing review writes the Markdown artifact, compacts the checkpoint to `complete`, and prints `DONE`.
