# Java profile

Top rule: Use concrete services and explicit value contracts.

## 1 Structure

- Default: organize by capability, not global controller/service/repository layers.
- Default: keep implementation classes and constructors package-private where
  callers need no access; expose intentional APIs and invariant-safe construction.
- Heuristic: add packages/modules only for a real boundary, not every capability.

## 2 Preferred

- Default: use records for values and concrete services with constructor injection.
- Requirement: declare and check nullability using the repository's supported scheme.
- Default: represent ordinary business outcomes as values, not exceptions.
- Default: use specific exceptions for operational failures; preserve causes.
- Requirement: use try-with-resources for owned closeable resources.
- Default: synchronous calls first; concurrency only for demonstrated need.
- Requirement: own concurrent work, cancel/shut down and join it, and observe
  failures; use supported structured APIs or explicit executor/future lifecycles.
- Heuristic: add interfaces only for real consumer contracts or substitution.

## 3 Disallowed

- Default: avoid interface-per-class, field injection, and redundant DTO chains.
- Requirement: do not hide nullability violations or swallow broad exceptions.
- Default: keep framework annotations out of business values where practical.

## 4 Canonical

Use repository code only when compliant with the adopted contract.
No bundled Java example.

## 5 Verification

Requirement: compile with diagnostics/nullability checks, test behavior, and check
package dependencies. Mechanical checks do not prove architecture.
Default: use repository-supported stable JDK/build tools; commands below are
fallbacks, not required dependencies. Do not require preview concurrency APIs.

```verify
./mvnw -q verify
```

Gradle repositories: replace with `./gradlew check` and equivalent configured checks.
Boundaries: `templates/boundaries/ArchitectureTest.java`
Requirement: brownfield baselines identify existing violations; reject new ones.
Use ArchUnit `FreezingArchRule` with reviewed frozen entries; do not automatically
accept new entries or blanket-skip packages. Exceptions follow `standards/contract.md`.
