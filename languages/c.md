# C profile

Top rule: Make ownership, output state, and undefined-behavior prevention explicit.

## 1 Structure

- Default: group APIs by capability; no mandatory directory or target per capability.
- Default: use opaque structs for private state and `static` internal functions.
- Heuristic: split headers/targets where a real consumer boundary warrants it.

## 2 Preferred

- Default: use the repository-supported stable standard; C17 is the conservative fallback.
- Default: return explicit status codes with out-parameters; specify output state
  on failure, partial progress, and whether the caller must release resources.
- Requirement: pair buffers with lengths/capacities; check bounds and termination.
- Requirement: document allocation ownership, borrowing, and release responsibilities.
- Requirement: check size arithmetic and conversions before allocation/indexing;
  prevent integer overflow, use-after-free, aliasing violations, and uninitialized reads.
- Default: use `const` borrowed inputs and fixed-width types at wire/storage edges.
- Default: synchronous calls first; concurrency only for demonstrated need.
- Requirement: own threads, signal shutdown, join, and observe failures.
- Default: use one cleanup path for acquired resources; cleanup `goto` is allowed.

## 3 Disallowed

- Requirement: no unbounded writes (`gets`, `strcpy`, `strcat`, `sprintf`).
- Requirement: bounded APIs still require truncation, size, and overflow checks.
- Default: avoid macro control flow and casts that hide ownership or constness.

## 4 Canonical

Use repository code only when compliant with the adopted contract.
No bundled C example.

## 5 Verification

Requirement: compile with strict warnings, analyze, format, and test with supported
sanitizers; check header/target dependencies. Tools do not prove architecture.
Default: use repository-supported stable tools; commands below are fallbacks,
not required dependencies. Configure warning and sanitizer flags in the build.

```verify
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel
ctest --test-dir build --output-on-failure
clang-tidy -p build $(git ls-files '*.c')
clang-format --dry-run --Werror $(git ls-files '*.c' '*.h')
```

Boundaries: `templates/boundaries/CMakeLists.layering.txt`
Lint config: `templates/boundaries/.clang-tidy`; cppcheck is an alternative analyzer.
Requirement: baseline existing diagnostics by rule/location; reject new findings.
Use reviewed, bounded suppressions, never blanket-skip targets or safety checks.
Exceptions follow `standards/contract.md`.
