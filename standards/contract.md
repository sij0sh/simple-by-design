# Style Contract v1

Apply these rules to every code change. Repository conventions
prevail unless they violate an architectural invariant.

## Defaults

- Keep behavior, state, and business rules in their owning module.
- Prefer straightforward control flow, composition, and explicit dependencies.
- Keep public APIs small and intentional.
- Keep transport and I/O adapters thin.
- Follow established naming and implementation patterns.
- Test observable behavior and invariants.
- Prefer deletion and localized changes over additional concepts.

## Architectural invariants

1. Module dependencies must remain acyclic.
2. Cross-module dependencies must use the owning module's
   declared public API, not internal implementations or
   directly accessed owned state.

## Design constraints

- Introduce architectural abstractions only for a concrete need,
  such as meaningful reuse or a real substitution requirement.
- Do not add packages, layers, or dependencies without justification.
- Avoid global mutable state, hidden dependencies, and unrelated refactors.

## Exceptions

Safety and correctness take precedence over style preferences.

Record the rationale for deviations. An exception to an
architectural invariant requires explicit justification and
approval. Temporary exceptions must include a revisit condition.

## Tie-breaker

Among correct solutions, prefer the one with the fewest new
concepts, closest to established patterns, and least context
required to understand it.
