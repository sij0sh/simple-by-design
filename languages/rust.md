# Rust profile

Top rule: Use ownership and types to keep invalid states local.

## 1 Structure

- Use a workspace with `crates/<capability>/`.
- Each crate exposes a small `lib.rs`. Keep the rest `pub(crate)`.
- Keep domain crates free of HTTP, database, and queue crates.
- Keep tests beside the module or under `tests/` for public behavior.

## 2 Preferred

- Model states with enums and make invalid combinations unrepresentable.
- Return `Result` with contextual errors.
- Define small traits at the consumer when substitution is real.
- Make ownership explicit. Prefer borrowing over cloning.
- Use `#[must_use]` where ignoring a result is a bug.
- Prefer plain functions and modules over trait hierarchies.
- Keep `unsafe` blocks small, justified, and tested.

## 3 Disallowed

- `unwrap` or `expect` on fallible library paths: exception only for a proven
  invariant with a message.
- `unsafe` without a safety comment: exception none.
- Mutable statics and hidden interior mutability: exception only for a
  documented process-wide cache with a reset for tests.
- Trait-per-struct without a substitution need: exception none.
- Domain dependencies on transport or storage crates: exception none.
- `clone` used to avoid ownership design: exception only at a boundary where
  sharing is real.
- Wildcard dependencies: exception only for internal workspace crates.

## 4 Canonical

Use comparable repository code first. No bundled Rust example.

## 5 Verification

```verify
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all
cargo deny check
```

Boundaries: none enforced by Cargo. Crate cycles fail by construction;
workspace layering is a review rule.
Dependency policy: `templates/boundaries/deny.toml`
Brownfield ratchet: none built in. Run Clippy without `-D warnings` and track
the count per crate.
