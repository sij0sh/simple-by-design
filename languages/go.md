# Go profile

Top rule: Prefer concrete structs, explicit errors, and owned goroutines.

## 1 Structure

- Default: group cohesive packages by capability; no package required per feature.
- Default: use `internal/` for private packages and minimal exported APIs.
- Heuristic: use `cmd/<name>/` when multiple binaries need separate entry points.

## 2 Preferred

- Default: use concrete structs; small interfaces belong to their consumers.
- Default: return explicit values and errors; wrap causes with `%w`.
- Requirement: inspect wrapped errors with `errors.Is`/`errors.As`, not strings.
- Requirement: pass `context.Context` through cancellable I/O paths.
- Default: synchronous calls first; start goroutines for demonstrated concurrency.
- Requirement: every goroutine has an owner, cancellation/shutdown path, join,
  and observed failure; cancellation alone does not wait for termination.
- Requirement: close owned resources, normally with `defer`; handle material
  `Close` errors, especially when they determine write success.

## 3 Disallowed

- Default: avoid interface-per-struct and unrelated `util`/`common` packages.
- Requirement: do not use `panic` for ordinary business or operational failures.
- Requirement: do not discard errors or leave goroutines unowned.

## 4 Canonical

Use repository code only when compliant with the adopted contract.
No bundled Go example.

## 5 Verification

Requirement: verify formatting, static diagnostics, behavior, and race safety;
check configured package boundaries. Mechanical checks do not prove architecture.
Default: use repository-supported stable tools; commands below are fallbacks,
not required dependencies. Formatting output must produce a failing exit status.

```verify
gofmt -l . > /dev/null && test -z "$(gofmt -l .)"
go vet ./...
golangci-lint run
go test -race ./...
```

Boundaries: `templates/boundaries/.golangci.yml`
Requirement: brownfield baselines identify existing violations; reject new ones.
Use `--new-from-rev` against a reviewed fixed revision, retaining full diagnostics;
never blanket-skip legacy packages. Exceptions follow `standards/contract.md`.
