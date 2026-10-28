# Rust profile

Top rule: Express state and ownership with types before adding abstractions.

## 1 Structure

- Default: group modules by capability; no crate or workspace required per feature.
- Default: expose small APIs; private items first, `pub(crate)` only when needed.
- Heuristic: split crates for real dependency, build, or distribution boundaries.

## 2 Preferred

- Default: use structs and enums for data, states, and business outcomes.
- Default: use typed `Result` for failure and `Option` for meaningful absence.
- Default: borrow before cloning; document ownership transfers at APIs.
- Heuristic: use traits for real contracts, not one trait per struct.
- Default: use `#[must_use]` where ignoring a value loses required work.
- Default: synchronous logic first; async only for an actual concurrency need.
- Requirement: own spawned tasks, cancel/shut down and join them, and observe
  failures; dropping a handle is not evidence of task termination.
- Requirement: keep `unsafe` small with documented safety invariants and tests.

## 3 Disallowed

- Requirement: no `unwrap`/`expect` on unproven fallible production paths.
- Default: avoid mutable statics and cloning to evade ownership design.
- Requirement: no undocumented unsafe invariants or unobserved task failures.

## 4 Canonical

Use repository code only when compliant with the adopted contract.
No bundled Rust example.

## 5 Verification

Requirement: format, lint, test, and check dependency policy and module boundaries.
Default: use repository-supported stable tools; commands below are fallbacks,
not required dependencies. Mechanical checks do not prove architecture.

```verify
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all
cargo deny check
```

Dependency policy: `templates/boundaries/deny.toml`; Cargo does not enforce
capability ownership or workspace layering. Review these separately.
Requirement: brownfield baselines identify existing findings by rule and location;
reject new findings, not merely count increases. Use scoped lint allowances
with owners/revisit conditions, never blanket-disable warnings or legacy crates.
Exceptions follow `standards/contract.md`.
