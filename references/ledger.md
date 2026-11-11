# Ledger contract

Python 3.11+, POSIX (`flock`, atomic rename); standard library only. Run `python3 "$S/scripts/sbd.py"` from the task project. Optional global `--root DIR` selects that project explicitly. Commands emit a JSON current view; errors use stderr and exit 2. Runtime performs no experiments or implementation.

State: `.agents/sbd-adaptive/TASK.json`. Task/record/criterion IDs: 1–64 lowercase letters, digits, `_`, `-`; first character alphanumeric. Task IDs are filenames, never paths.

## Small unambiguous example

This designs a greeting; it does not implement anything or invent questions. Request-derived evidence supports a design-level comparison, not a runtime test claim.

```sh
python3 "$S/scripts/sbd.py" new greeting <<'JSON'
{"request":"Design a greeting that returns exactly Hello.","constraints":[],"permissions":["Read this request; design only"],"criteria":[{"id":"exact","text":"Design specifies exactly Hello, with no extra text"}],"independent_review":false}
JSON
python3 "$S/scripts/sbd.py" record greeting --at 1 <<'JSON'
{"type":"evidence","id":"request","kind":"documented","authority":"requester","source":"Current request","claim":"Return exactly Hello, no extra text"}
JSON
python3 "$S/scripts/sbd.py" record greeting --at 2 <<'JSON'
{"type":"design","id":"solution","text":"Return the constant string Hello, without punctuation or newline.","verification":"During implementation assert exact string equality to Hello.","depends_on":["request"]}
JSON
python3 "$S/scripts/sbd.py" record greeting --at 3 <<'JSON'
{"type":"check","id":"exact-check","criterion":"exact","design":"solution","result":"passed","evidence":["request"],"explanation":"The candidate specifies exactly the requested string; no implementation is claimed."}
JSON
python3 "$S/scripts/sbd.py" finish greeting --at 4 <<'JSON'
{"revision":4,"reviewer":"local review; no independent reviewer available","independent":false,"reviewed":["request","constraints","permissions","evidence","decisions","questions","design","checks"],"findings":[]}
JSON
```

The final view is revision 5, `status: complete`, `completion.certifies: 4`.

## Inputs

`new TASK`: exactly `request` (text), `constraints` (text list), `permissions` (text list), `criteria` (nonempty list of `{id,text}`), `independent_review` (boolean). Criteria are **design** acceptance checks, not future implementation test results. All criteria are required and immutable. A materially different goal uses a new task.

`record TASK --at R`: one object, required `type` and unique `id`. Optional `depends_on` lists earlier record IDs. Unknown fields, empty required text, duplicates, invalidated/missing references, and forward/self references are rejected. Earlier-only references make dependency cycles impossible. All records and implicit dependencies appear in `show`.

| Type | Additional required fields |
| --- | --- |
| `evidence` | `kind`, `authority`, `source`, `claim` |
| `question` | `text`, `kind` (`intent`/`fact`/`choice`), matching `resolver`, structured `witness`, `consequence`, `required` boolean, `next` |
| `answer` | `question` ID, `text`, matching `resolver`, nonempty `evidence` ID list, `mode` (`established`/`provisional`); see below |
| `defer` | `question` ID, `boundary`, `owner`, `reason`, `trigger`, nonempty `evidence` IDs |
| `design` | `text`, `verification` (future implementation verification plan) |
| `check` | `criterion` ID, current `design` ID, `result` (`passed`/`failed`), nonempty `evidence` IDs, `explanation` |
| `evaluation` | Same evaluation fields as `finish`; revision must equal pre-event head |
| `pause` | `reason`, `needs` (needed resolver/authority/evidence) |
| `reopen` | Nonempty `targets` IDs, `trigger`, inline `cause` evidence object |

Evidence combinations:

| `kind` | Allowed `authority` |
| --- | --- |
| `observed` | `observation`, `requester` |
| `documented` | `project`, `requester` |
| `inferred` | `inference` |
| `unknown` | `unknown` |

`source` cites request words, document, path:lines, command/result, etc. `claim` states exactly what that source establishes. `unknown` can preserve a missing basis but cannot support an answer or check. A check may cite explicit reasoned inference for **design** properties; that does not establish a runtime fact.

### Questions and answers

Resolvers: intent → `requester`; fact → `observation`; choice → `policy`.

Witness forms (all shown fields required):

```json
{"form":"pair","a":"Outcome A","b":"Outcome B","difference":"Why requester/criterion distinguishes them"}
{"form":"defeater","claim":"Relied-on claim","condition":"Plausible unexcluded condition","impact":"Changed outcome"}
{"form":"check","criterion":"declared-criterion-id","failure":"Missing/contradicted check"}
```

Questions may depend only on earlier questions, including unresolved ones. Answering requires those dependencies already resolved/provisional. Designs/evidence/checks may cite resolved/provisional questions as dependencies. No references to nonexistent future records.

- Established intent: all supporting evidence requester-sourced. Never provisional.
- Established fact: all supporting evidence `observed`; this may include a requester-sourced factual observation, not an intent preference used as a fact. Inference cannot be promoted by an answer status.
- Choice: also requires `policy`, `alternatives` (nonempty `{option,rejected_because}` list), `rationale`, `tradeoff`, `revisit`. Policy levels: `requirements`, `decisions`, `conventions`, `defaults`, `contract`, `language`, `instructions`, `simplest`. Requirements need requester evidence; other named policies need documented project evidence; simplest may use explicit inference. The agent must honor semantic precedence and verify relied-on assumptions; enum validation does not prove it did so.
- Provisional fact/choice: also `reversal`, `detect`, `revisit`; cite explicit `inferred` evidence. These state why a wrong pick is cheap to undo and would be noticed. `established` on a choice means adopted engineering decision, not an observed world fact.
- Deferral: only `required: false` questions, with requester-sourced evidence of the outside-current-design boundary. A deferred question is not usable evidence for another answer/design. All open questions block completion, including optional ones until explicitly disposed of.

Replacing an answer uses a **new answer ID** for the same question. It automatically invalidates the old resolution and transitive dependents. Replacing evidence instead requires explicit reopening; merely adding a contradictory record does not make the CLI detect a semantic contradiction. A new design invalidates the old design/checks; a new check replaces the previous check for that criterion/current design. Record all relied-on dependencies; omitted ones cannot be discovered by schema validation.

### Evaluation and completion

`finish TASK --at R` stdin:

```json
{"revision":12,"reviewer":"Reviewer identity and review mode","independent":false,"reviewed":["request","constraints","permissions","evidence","decisions","questions","design","checks"],"findings":[]}
```

`revision` must equal R and current head; the example's `12` is illustrative. All eight review subjects required. `findings` names existing question IDs; record newly discovered questions before a non-final `evaluation`. Non-final evaluations are historical findings, not reusable completion tokens. Final findings must be empty.

Read a stable snapshot with `show TASK --at R --history`. Pass that snapshot, not only a narrative, to an independent critic when available. Final evaluation and completion are appended in **one** event at R+1, certifying parent R. No self-evaluation paradox. Any intervening event requires a fresh review. Do not update an old evaluation's number without re-evaluating.

Completion requires active status, a current design, every criterion passed for that design, no open/required-deferred question, and required reviewer independence. A pause is blocked, never complete. A subsequent ordinary record resumes active status; resolve the stated blocker, not merely its status flag. No retry count can authorize success.

### Reopening

Ordinary mutation after completion is refused. Reopen the same request explicitly:

```json
{"type":"reopen","id":"new-observation","targets":["solution"],"trigger":"contradiction","cause":{"kind":"observed","authority":"observation","source":"Authorized observation, command/result or path:lines","claim":"What contradicts the relied-on basis"}}
```

Triggers: `contradiction`, `revisit`, `uncheckable`, `intent-choice`. Cause must be observed/documented, not inferred/unknown. Targets: evidence, question, answer, deferral, design, or check. Dependents invalidate transitively; affected questions reopen, completion clears, historical events remain. This event grants no new permissions and does not change the request or criteria.

## Persistence and assurance limits

Writers hold a per-task POSIX lock, check expected revision under that lock, validate, write/fsync a private temp file, atomically replace, then fsync the directory. Readers replay-validate one atomic snapshot without locking. Process death releases locks; lock files are intentionally never unlinked. Interrupted writes may leave ignored temp files, never a partially written target. A failure after rename may mean the new state is visible; reload before retrying.

Logical history is append-only inside an atomically rewritten JSON document, not a cryptographically authenticated log. Corrupt/unsupported histories fail closed; `new` never overwrites one. Task and lock symlinks/nonregular files are rejected; this is not a sandbox against a hostile actor controlling parent directories. No source authenticity, semantic truth, omitted-dependency detection, tool-permission enforcement, or proof of completeness is claimed.
