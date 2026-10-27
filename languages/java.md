# Java profile

Top rule: Minimize unnecessary abstraction layers.

## 1 Structure

- Package by capability: `orders`, `billing`, `users`.
- Keep implementation classes package-private. Export intentional APIs.
- Keep persistence and transport adapters out of domain packages.
- Put tests in the same package as the code they exercise.
- Avoid global `controllers`, `services`, and `repositories` packages.

## 2 Preferred

- Use records and immutable value objects for data that should not change.
- Use constructor injection.
- Define transaction boundaries in one explicit place.
- Prefer concrete services until substitution is real.
- Keep domain rules free of framework annotations where practical.
- Return small result types instead of deep DTO chains.

## 3 Disallowed

- One interface per class: exception only for a real substitution or boundary.
- Deep inheritance: exception only where a framework requires the hierarchy.
- Excess DTO mapping between layers: exception only at a serialization
  boundary that needs a different shape.
- Global layer packages: exception none.
- Field injection: exception only in framework-managed test fixtures.
- Domain dependencies on web, ORM, or messaging APIs: exception none.

## 4 Canonical

Use comparable repository code first. No bundled Java example in 0.1.0.

## 5 Verification

```verify
./mvnw -q verify
```

Gradle repositories: replace with `./gradlew check`.
Boundaries: `templates/boundaries/ArchitectureTest.java`
Brownfield ratchet: ArchUnit `FreezingArchRule`
