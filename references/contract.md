# Ownership and boundary contracts

- Access each state/rule through its owner; no second authoritative copy.
- Dependencies point one way. A cycle needs a cohesive owner or explicit boundary.
- Every resource has an owner for cleanup, completion/cancellation, and observing failure.
- Expose inputs, outputs, errors, effects, and lifetime at trust boundaries.
- Prefer local duplication across unrelated capabilities over unnecessary coupling.
- Judge complexity by concepts and owners touched, not lines or file count.
