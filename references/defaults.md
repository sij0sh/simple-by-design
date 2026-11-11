# Design defaults

Only after requirements, established decisions, and conventions leave a choice open:

- Smallest conventional adequate solution; abstractions need a present responsibility.
- One authoritative owner per behavior, rule, and mutable state.
- Plain data/functions; reason locally from owner, inputs, dependencies.
- Validate at trust boundaries; state inputs, outputs, errors, effects, and lifetimes.
- Among equally adequate choices, prefer conventional and reversible.
