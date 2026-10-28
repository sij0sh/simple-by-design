// Consumer contract tests: imports only the declared api/ directory.
import { expect, it } from "vitest";
import { quoteOrder, type OrderRepository } from "../src/modules/orders/api/quote-order";

const orders: OrderRepository = {
  findById: (id) => id === "o1" ? {
    id,
    lines: [{ sku: "a", unitCents: 6699, quantity: 1 }],
    discountPercent: 15,
  } : undefined,
};

it("quotes via the public contract", () => {
  const result = quoteOrder(orders, "o1");
  expect(result.kind).toBe("quoted");
  if (result.kind !== "quoted") throw new Error("expected a quote");
  expect(result.quote).toEqual({ orderId: "o1", totalCents: 5694 });
});
it("rejects invalid ids", () => {
  expect(() => quoteOrder(orders, " ")).toThrow("non-empty");
});
it("reports missing orders", () => {
  expect(quoteOrder(orders, "missing")).toEqual({ kind: "not-found" });
});

it("propagates repository failures unchanged", () => {
  const failure = new Error("repository unavailable");
  const repo: OrderRepository = { findById: () => { throw failure; } };
  expect(() => quoteOrder(repo, "o1")).toThrow(failure);
});
