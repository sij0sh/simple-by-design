# Go profile

Top rule: Prefer simple composition and small interfaces.

## 1 Structure

- Put binaries in `cmd/<name>/` and private code in `internal/`.
- Group packages by capability, not by technical layer alone.
- Keep a package cohesive. Its name should state one responsibility.
- Export only what another package needs. Prefer `internal/` for the rest.
- Keep domain packages free of transport and database packages.

## 2 Preferred

- Use small interfaces owned by the consumer.
- Return concrete types unless a boundary needs substitution.
- Wrap errors with context using `%w`.
- Give every goroutine a lifetime, cancellation path, and owner.
- Pass `context.Context` through I/O paths.
- Prefer plain functions and structs over framework machinery.

## 3 Disallowed

- `util`, `common`, or `types` dumping grounds: exception only for a named,
  cohesive infrastructure package.
- Java-style interface per type: exception only for a real substitution need.
- `panic` for routine errors: exception only for an impossible invariant at
  startup.
- Goroutines without cancellation or shutdown: exception only for a
  process-lifetime worker with an explicit stop path.
- Domain imports of HTTP, SQL, or queue packages: exception none.

## 4 Canonical

Use comparable repository code first. No bundled Go example in 0.1.0.

## 5 Verification

```verify
gofmt -l .
go vet ./...
golangci-lint run
go test -race ./...
```

Boundaries: `templates/boundaries/.golangci.yml`
Brownfield ratchet: golangci-lint `--new-from-rev`
