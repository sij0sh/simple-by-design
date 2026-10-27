# Style Contract v1

Apply this contract to every code change. Read `standards/local-reasoning.md`
for the rationale.

## Required defaults

- Put behavior in the module that owns it.
- Prefer straightforward functions and composition.
- Make dependencies and side effects explicit.
- Keep public APIs small and intentional.
- Keep business logic separate from I/O.
- Follow local naming and patterns.
- Test behavior and invariants.

## Avoid by default

- Speculative abstractions and generic frameworks.
- Inheritance and wrapper layers with no concrete need.
- Global mutable state and hidden dependencies.
- Circular or undocumented coupling.
- Grab-bag utility modules.
- New packages when existing modules suffice.
- Unrelated refactors during feature work.

## Enforceable constraints

1. No module cycles.
2. No access to another module's internals or owned data without a contract.
3. No business logic in transport handlers.
4. No abstraction without demonstrated value: repeated use or real
   substitution.
5. No exception without a rationale and a revisit plan.

## Implementation rules

- Match existing architecture unless it breaks a mandatory invariant.
- Prefer deletion or simplification over expansion.
- Never broaden a public API without justification.

## Exceptions

Safety and correctness win. A style rule may be overridden when the change
demonstrates a simpler solution and records the reason.

## Tie-breaker

When several correct implementations exist, choose the one with the fewest new
concepts, closest to existing patterns, and least context needed to understand
it.
