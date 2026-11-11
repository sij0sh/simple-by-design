# 0002. Standard-library-only POSIX runtime

- Status: accepted (retroactive)
- Date: 2026-11-11

## Context

`README.md` requires Python 3.11+ and POSIX (`flock`, atomic rename) with no dependencies. `scripts/engine/state.py` imports `fcntl` and relies on `os.replace`, directory `fsync` and `O_NOFOLLOW`. Tests use only `unittest`.

## Decision

Keep `scripts/` standard-library-only and POSIX-only, with Python 3.11 as the supported floor. Runtime dependencies stay at zero; `mise.toml` pins only the development toolchain (Python and ruff), and `mise.lock` records it.

## Consequences

- The skill runs from a checkout without an install step or package manager.
- Windows is unsupported because the state owner needs POSIX locking and rename semantics.
- Tooling changes require updating `mise.toml` and committing `mise.lock`; runtime code must not import third-party packages.
- Reviewers must keep new scripts inside the standard library and the 3.11 floor.
