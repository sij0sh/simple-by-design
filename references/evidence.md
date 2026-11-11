# Evidence policies, not task processes

Use only policies relevant to a surviving witness or required design check.

| Claim | Sufficient kind of support / critical counterexample |
| --- | --- |
| Desired behavior or permission | Requester or authoritative requester document. Engineering convenience cannot establish intent. |
| Current capability / defect | Inspect cited implementation and callers; observe relevant behavior where authorized. A symptom or name alone is insufficient. |
| Behavior-preserving refactor | Identify observable contract, side effects, failure behavior, and callers; compare old/new semantics. Fewer lines do not establish equivalence. |
| Incident cause | Discriminating observations against viable rivals. Correlation, plausible mechanisms, and inability to reproduce stay conditional. |
| Architecture choice | Current constraints, strongest viable alternative, ownership/boundaries, tradeoff, revisit. Not hypothetical future scale alone. |
| Security finding | Assets, principals, trust boundaries, attacker prerequisites, actual controls, reachability, and impact. Missing deployment evidence keeps exploitability conditional; do not perform unauthorized exploitation. |
| Instruction improvement | A specific changed decision and observable result, including an unfamiliar case and a precise negative control. Fixtures alone are not behavioral evidence. |
| Design readiness | Candidate meets stated design criteria with cited analysis/evidence. Future implementation tests remain a verification plan, not passing results. |

Evidence records distinguish `observed`, `documented`, `inferred`, `unknown`, with source and claim. Reading a document observes its contents, not necessarily the truth of all its claims. Requester documents may establish intent; world claims need the appropriate observation. Do not relabel inference to satisfy a validator.

The ledger cannot discover omitted dependencies or authenticate citations. Record every relied-on basis; a fresh critic must also look beyond the planner's selected evidence. Report review independence, observations actually performed, unsupported claims, and remaining uncertainty honestly.
