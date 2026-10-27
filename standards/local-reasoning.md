# Local Reasoning - Coding Style v1.0

This file explains why the style exists. `standards/contract.md` holds the
rules. Language profiles only add or specialize, never repeat.

## Governing sentence

Optimize for local reasoning. A developer should be able to understand, change,
and test a business capability without understanding the entire system.

## Principles

1. Localize. Keep related data, behavior, and decisions together.
2. Expose. Make dependencies, state, ownership, and side effects visible.
3. Minimize. Use the fewest abstractions and concepts that solve the problem.
4. Standardize. Solve similar problems with consistent patterns.
5. Verify. Make boundaries and behavior cheap to check.

## Standards

1. Clear boundaries. Group code by business capability. A module owns one
   responsibility, and its name says which one.
2. One-way dependencies. Predictable direction stops a local change from
   rippling through unrelated modules.
3. Explicit over implicit. Visible flow and dependencies let a reader follow
   the code without reconstructing hidden state.
4. Locality of change. Most features should fit in one module; the need to
   edit many modules usually means ownership is wrong.
5. Single source of truth. One owner per business rule, calculation, and piece
   of state keeps behavior predictable and edits cheap.
6. Abstraction earns its place. Every new interface, factory, or base class is
   a concept a reader must hold; repeated use or a real substitution need pays
   for it.
7. Consistency over cleverness. Familiar patterns reduce review cost and make
   defects stand out.
8. Business and infrastructure split. Domain rules stay readable without
   knowing HTTP, queues, databases, or framework internals.
9. Test behavior. Observable outcomes and invariants survive refactors;
   tests bound to internals make every change expensive.
10. Delete before adding. Removing obsolete paths and needless machinery is
    usually safer than extending them.

## Measures

- Change surface: modules and files that must change for one feature.
- Cognitive load: how much of the system a developer must hold to work safely.
- Coupling: how many modules can break from one change.
- Discoverability: how quickly a developer can find where behavior belongs.
- Predictability: whether code behaves as its structure and names suggest.
- Deletion cost: whether unused functionality can leave without a hunt.

## Capability layout

```
src/
  modules/
    <capability>/
      api/
      domain/
      persistence/
  shared/
    logging/
    database/
    config/
```

`shared/` holds cross-cutting infrastructure only. It is not a dumping ground
for code that has no owner. A capability owns its business rules and exposes a
small, intentional interface.

## Closing

Simple means cheap to understand and change, not short.
