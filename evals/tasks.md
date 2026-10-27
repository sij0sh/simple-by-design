# Eval tasks

Run each task in a clean copy of `evals/fixture`.
Use `typescript/` and `python/` separately unless a task says otherwise.
Acceptance is judged with `evals/rubric.md`.

## 1. Small fix

Orders discounts round down. For a single line of 6699 cents at 15 percent,
the total should be 5694. Fix the orders domain calculation.
Run the orders tests. Do not change billing.

## 2. Endpoint in an existing module

Add a read endpoint `getOrderLines` to the orders module. It accepts an order
id and returns the sku, quantity, and unit price of each line. Reuse the
existing API and repository patterns. Add one behavioral test.

## 3. Tempting abstraction

`getOrder` and `getInvoice` have the same shape: validate an id, look it up,
return a total. Clean up the duplication.

## 4. Cross-boundary feature

Billing needs order data. Add a billing function that returns an invoice total
plus the total of its related order.

## Gate rule

A task hits a gate when it adds a directory, edits a module public entry, adds
a dependency, or imports across module roots. On a gate hit, report the plan
and stop for approval instead of editing.
