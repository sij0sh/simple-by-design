# 0001. Fixed prompt dispatcher instead of a design ledger

- Status: accepted (retroactive)
- Date: 2026-11-11

## Context

The original adaptive skill kept a persistent design ledger and let the agent choose the next workflow step. Commit `c840d9d` replaced that with a focused dispatcher; `README.md` now states there is no workflow selection or ledger maintenance. `scripts/engine/router.py` defines one fixed transition table and opaque tickets.

## Decision

`engine/router.py` owns the prompt sequence and result shapes. `draft` returns `candidate` or `need`; `resolve` returns `resolved` or `blocked`; `review` returns `pass`, `revise` or `need`. Each non-pass result issues a new opaque ticket. The checkpoint is one JSON document at `.agents/sbd-adaptive/run.json`; there is no ledger module or revision history API.

## Consequences

- The agent cannot select a workflow or append ledger entries; the CLI prints exactly the next prompt.
- Stale, duplicate and out-of-order results are rejected instead of recorded.
- Checkpoint schema 1 is refused; users move `run.json` aside to start fresh.
- Design history is limited to the current candidate, accumulated resolutions and review feedback.
