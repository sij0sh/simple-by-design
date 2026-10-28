# Eval tasks

Run independent clean copies; use TypeScript and Python separately. Record
revision, tools, baseline checks, approval decisions, final diff and checks.
Score completed changes with `rubric.md`; stopping for approval is not completion.

## Approval setup

Before each run, approve and record repository defaults once: owner/API map,
allowed dependency direction, state ownership, selected verification entrypoint
and coverage. Inspect existing config before adoption; approved config owns
mechanical details. Record justified deviations; profile commands are fallbacks.
Directory creation alone is not a gate. Ask only for an unapproved architectural
choice (owner, public contract, dependency direction, state owner, or policy).
Continue after the evaluator answers; record that answer.

## 1. Legacy scoped fix

Copy `fixture/`; run `fixture/seed-small-fix.sh <copy>`. Capture baseline failures.
Orders discounts round down; 6699 cents at 15 percent must total 5694. Fix orders,
add a regression assertion, leave billing unchanged. Run baseline and final checks,
including failing checks: distinguish the seeded failure, unrelated baseline
failures, unavailable checks, and introduced regressions. No new violations;
no global cleanup. Removing a check or accepting every failure is not a baseline.

## 2. Greenfield feature

Start an empty project in either language. Implement order quotes from lines
(unit cents and quantity) and a percentage discount, returning integer cents.
Accept 0-100 percent; reject negative prices, nonpositive quantities and invalid
discounts. Define the rounding contract explicitly. Test 0/100 percent, invalid
inputs and 6699 at 15 percent -> 5694. Select and record tools/coverage first.
Ownership and contract must be identifiable without mandatory layers, repositories,
interfaces, or directories. A single cohesive implementation can pass.

## 3. Second real variation

Continue task 2. Add a fixed-cent discount alongside percentage discount. Clamp
fixed discounts at subtotal; reject negative discounts. Keep existing percentage
behavior and API compatibility; add tests for both variants and overlarge fixed
discounts. Judge whether the resulting design is understandable locally, not
whether an abstraction was introduced. Leave unrelated code untouched.

## 4. Boundary change

Copy `fixture/`. Billing needs invoice total plus the total of its related order.
Declare/approve the orders contract and billing -> orders direction first.
Implement through the declared API, not orders internals; test success, unknown
invoice and unknown order. Orders owns order data; billing owns invoice data.
Verify unchanged existing behavior and no reverse edge/cycle. Consumers must be
able to use contract input types without importing undeclared implementation.

## 5. Existing owner extension

Copy `fixture/`. Add `getOrderLines` / `get_order_lines`, returning sku, quantity
and unit cents. Extend the declared orders API with approval if not already
covered; test success and invalid/missing IDs. Billing stays unchanged.

## Interpretation

Requirements: acyclic dependencies, declared APIs, owned state, behavior/tests,
no new violations. Defaults: repository-selected layout/tools, approved once.
Heuristics: diff size, duplication, abstraction count; inspect, do not gate on them.
Historical `results/` runs used obsolete stop-at-gate rules. They do not evaluate
these tasks or demonstrate long-term maintainability. Rerun before comparing.
