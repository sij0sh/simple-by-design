# Boundary config checks

Date: 2026-10-27

The TypeScript and Python starter configs were run against the eval fixture.
Each allowed the clean fixture and caught one seeded cross-module import.

## dependency-cruiser

Config: `templates/boundaries/.dependency-cruiser.cjs`

```
depcruise src
# clean: 12 modules, 6 dependencies, no violations
# seeded billing -> orders/domain: 1 error
```

## Import Linter

Config: `templates/boundaries/.importlinter`

```
PYTHONPATH=src lint-imports
# clean: 1 contract kept
# seeded billing -> orders/domain: 1 contract broken
```

Go and Java configs were not executed in this environment. Go import cycles
are rejected by the compiler. Java requires a project with ArchUnit on the
test classpath.
