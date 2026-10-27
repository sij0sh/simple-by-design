# C profile

Top rule: Keep interfaces small, ownership obvious, and undefined behavior out.

## 1 Structure

- Put one public header per capability in `src/<capability>/`.
- Keep private headers in `src/<capability>/internal/`.
- Use opaque structs for state that callers do not need to inspect.
- Use one build target per capability.
- Domain targets do not link transport or storage libraries.
- Keep tests in `tests/<capability>/`.

## 2 Preferred

- Follow the repository C standard. Use C17 for new code.
- Use fixed-width types at wire and storage boundaries.
- Return an explicit status or error code.
- Apply `const` correctness to pointer parameters.
- Give every allocation one documented owner.
- Keep internal functions `static`.
- Use checked buffer APIs and pass buffer sizes.
- Build with warnings as errors and sanitizers in tests.

## 3 Disallowed

- Mutable globals: exception only for documented process-wide configuration
  with a reset for tests.
- `strcpy`, `strcat`, `sprintf`, or `gets`: exception none. Use bounded
  alternatives.
- Allocations with an undocumented owner: exception none.
- Macro-based control flow: exception only for build configuration.
- Casting away `const`: exception only at a checked ABI boundary.
- Including another module's `internal/` headers: exception none.
- Undefined behavior such as signed overflow or strict-aliasing violations:
  exception none.
- Implicit function declarations and uninitialized values: exception none.

## 4 Canonical

Use comparable repository code first. No bundled C example.

## 5 Verification

```verify
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel
ctest --test-dir build --output-on-failure
clang-tidy -p build $(git ls-files '*.c')
clang-format --dry-run --Werror $(git ls-files '*.c' '*.h')
```

Use `cppcheck` when the build cannot produce a compile database.
Boundaries: `templates/boundaries/CMakeLists.layering.txt`
Lint config: `templates/boundaries/.clang-tidy`
Brownfield ratchet: warning baseline in the build, or a cppcheck suppress file.
