# C# profile

Top rule: Keep capability boundaries explicit and framework types out of the domain.

## 1 Structure

- Put each capability in its own project under `src/<Capability>/`.
- Keep transport and persistence adapters in separate projects.
- Make intentional types public. Keep the rest `internal`.
- Keep tests in `<Capability>.Tests`.
- Avoid global `Controllers`, `Services`, and `Repositories` folders.

## 2 Preferred

- Enable nullable reference types and treat warnings as errors.
- Use records and immutable value objects for data that should not change.
- Use constructor injection.
- Pass `CancellationToken` through async call paths.
- Keep one explicit transaction boundary per operation.
- Return small result types instead of deep DTO chains.
- Keep framework annotations out of the domain where practical.

## 3 Disallowed

- One interface per class: exception only for a real substitution or boundary.
- Deep inheritance: exception only where a framework requires the hierarchy.
- Field injection: exception only in framework-managed test fixtures.
- Service locator: exception only for an existing framework entry point.
- DTO mapping between every layer: exception only at a serialization boundary.
- Domain dependencies on ASP.NET, EF Core, or messaging types: exception none.
- `async void`: exception only for an event handler.
- Suppressed nullable warnings without a narrow reason: exception none.

## 4 Canonical

Use comparable repository code first. No bundled C# example.

## 5 Verification

```verify
dotnet build --nologo -warnaserror
dotnet format --verify-no-changes
dotnet test --nologo
```

Boundaries: `templates/boundaries/ArchitectureTest.cs`
Brownfield ratchet: `WarningsNotAsErrors` baseline in `.editorconfig`
