# Preflight

Run before editing. Read `standards/contract.md` for rules. Read
`standards/local-reasoning.md` when ownership or a boundary is unclear.

## Checks

1. Owning module identified. Name the module that owns the behavior.
2. Canonical implementation inspected. Prefer comparable repository code.
   Use `examples/reference-feature/` only in a greenfield repo or when no
   comparable code exists.
3. Language profile loaded. Read `languages/<language>.md`. If the language
   has no profile, apply the standards only and say so in the report.
4. New abstractions justified. Name the repeated use or real substitution.
5. Affected boundaries listed. Public entries, module roots, manifests.
6. Verification commands selected. Prefer the repo entry point. Otherwise use
   the profile `verify` block.

## Gate triggers

Any hit requires a written plan and approval before editing.

- New directory under a module root.
- Edit to a module public entry: `index.ts`, `__init__.py`, an exported Go
  package, or a public Java API.
- New entry in a dependency manifest.
- Import that crosses module roots.

No hit: run the checks silently and continue.

## Plan output

```markdown
## Plan

- Smallest change:
- Files touched:
- Boundaries crossed:
- Dependencies added:
- Tests:
- Exceptions:
```
