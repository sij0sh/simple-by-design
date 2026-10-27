# C++ profile

Top rule: Make ownership, lifetime, and target dependencies explicit.

## 1 Structure

- Put capability code in `src/<capability>/` and public headers in
  `include/<capability>/`.
- Keep internal headers in `src/<capability>/detail/`.
- Use one build target per capability.
- Domain targets do not link transport or persistence targets.
- Keep tests in `tests/<capability>/`.

## 2 Preferred

- Use RAII for every resource.
- Prefer value semantics and `std::unique_ptr` for exclusive ownership.
- Use `std::string_view` and `std::span` for non-owning parameters.
- Use `enum class` and `constexpr` instead of macros.
- Mark ignored results with `[[nodiscard]]`.
- Prefer composition over inheritance.
- Build with `-Wall -Wextra -Wpedantic` and sanitizers in tests.

## 3 Disallowed

- Owning raw pointers and explicit `new` or `delete`: exception only in a
  contained low-level adapter.
- Mutable globals and singletons: exception only for a documented
  process-wide service with a reset for tests.
- `using namespace` in headers: exception none.
- Including another module's `detail/` or private headers: exception none.
- C-style casts: exception only at a checked ABI boundary.
- Macros for constants, functions, or control flow: exception only for build
  configuration.
- Exceptions for routine control flow: exception only at a boundary that must
  translate errors.
- Uninitialized members: exception none.

## 4 Canonical

Use comparable repository code first. No bundled C++ example.

## 5 Verification

```verify
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel
ctest --test-dir build --output-on-failure
clang-tidy -p build $(git ls-files '*.cpp' '*.cc')
clang-format --dry-run --Werror $(git ls-files '*.cpp' '*.cc' '*.hpp' '*.h')
```

Boundaries: `templates/boundaries/CMakeLists.layering.txt`
Lint config: `templates/boundaries/.clang-tidy`
Brownfield ratchet: warning allowlist in `.clang-tidy`; remove per module.
