# Simple by Design

> **Complexity is easy. Simple is hard.**

Simple by Design is a coding-agent skill built around a predetermined coding style. It helps developers and coding agents make consistent, deliberate codebase decisions without reconsidering the same architectural questions for every change.

The goal is to reduce the cognitive load required to make good decisions.

**Simple doesn't mean less code. It means less unnecessary complexity to understand, change, and verify.**

## Why it exists

Every code change creates decisions:

- Where should this behavior live?
- Should this become a new abstraction?
- Which module should own this rule or state?
- How should dependencies flow?
- Should this follow an existing pattern or introduce a new one?
- What needs to be tested?

Without shared defaults, these decisions are repeatedly made from scratch. Different developers and agents may reach different answers, creating inconsistency, unnecessary abstractions, and harder-to-maintain boundaries.

Simple by Design establishes preferred answers to common questions.

This doesn't eliminate judgment. It reserves judgment for decisions that actually matter.

## The principle: Local Reasoning

Local Reasoning is the coding philosophy behind Simple by Design:

> A developer should be able to understand, change, and test a business capability without understanding the entire system.

It prioritizes five principles:

1. **Localize** — Keep related data, behavior, and decisions together.
2. **Expose** — Make dependencies, ownership, state, and side effects visible.
3. **Minimize** — Introduce the fewest concepts and abstractions needed to solve the problem well.
4. **Standardize** — Solve similar problems with consistent, familiar patterns.
5. **Verify** — Make boundaries and behavior straightforward to check.

These principles favor clear ownership, predictable dependencies, small intentional interfaces, and behavior-focused tests.

They do not prescribe arbitrary limits on lines, files, classes, or functions.

## How it works

Simple by Design guides a coding agent through a consistent workflow.

1. **Understand.** Identify the module that owns the behavior and inspect comparable code.
2. **Plan.** Choose the smallest appropriate change, identify affected boundaries, and select verification commands.
3. **Check.** Evaluate architectural risks before implementation. Changes that cross defined architectural gates require a plan and approval; routine changes proceed without unnecessary ceremony.
4. **Implement.** Follow established patterns, preserve clear ownership, and avoid unjustified complexity.
5. **Verify.** Run relevant tests and checks, review the resulting diff, and report exceptions or skipped verification.

The intent is not to maximize planning or minimize every diff. It is to apply the right amount of scrutiny to each change.

## What makes it different

Simple by Design treats coding style as a **decision-making policy**, not just a list of formatting preferences.

- **Defaults over repeated debate.** Common design choices have a consistent starting point.
- **Local changes over widespread coordination.** A feature should generally remain within its owning capability.
- **Justified abstractions over speculative ones.** New concepts must provide a concrete benefit.
- **Consistency over cleverness.** Familiar patterns reduce the effort needed to understand and review code.
- **Verification over trust alone.** Use automated checks wherever rules can be enforced objectively.

The smallest diff is not always the best solution. The preferred solution is the one that solves the problem correctly while introducing the least unnecessary complexity.

## What's included

- `SKILL.md` — the agent entry point and workflow routing.
- `standards/contract.md` — the authoritative coding and architecture rules.
- `standards/local-reasoning.md` — the rationale behind the style.
- `languages/` — language-specific guidance where available.
- `workflows/preflight.md` — checks before implementation and architectural approval gates.
- `workflows/review.md` — post-change review and completion criteria.
- `scripts/verify.sh` — the verification entry point.

The skill description is intended to be the entry point, rather than requiring a separate repository-level `AGENTS.md` or `CLAUDE.md`. Make sure your coding agent supports and discovers skills in the environment where you use it.

When a language profile is unavailable, the agent applies the universal standards and reports the limitation.

## Guidance is not enforcement

Agent instructions help guide decisions, but instructions alone cannot guarantee architectural compliance.

Use static analysis, tests, dependency-boundary checks, and CI where appropriate to enforce objectively verifiable rules. Keep subjective design judgments as review questions rather than pretending every preference can be reduced to a lint rule.

## The intended outcome

A codebase where developers can make sound changes with less context, fewer unnecessary decisions, and less risk of unintended consequences.

**The goal isn't to make every decision for the developer. It's to stop making them repeatedly decide things that should already have a clear answer.**
