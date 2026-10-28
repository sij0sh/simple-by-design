import { describe, expect, it } from "vitest";
import { quoteOrder } from "../src/modules/orders/api/quote-order";
import type { Order } from "../src/modules/orders/domain/order";
import { totalCents } from "../src/modules/orders/domain/pricing";
import { InMemoryOrderRepository } from "../src/modules/orders/persistence/order-repository";

const order: Order = {
  id: "o1",
  lines: [{ sku: "a", unitCents: 6699, quantity: 1 }],
  discountPercent: 15,
};

describe("order total", () => {
  it("applies a rounded discount to the subtotal", () => {
    expect(totalCents(order)).toBe(5694);
  });
});

describe("quote order", () => {
  it("returns the total for a stored order", () => {
    const repo = new InMemoryOrderRepository([order]);
    expect(quoteOrder(repo, "o1")).toEqual({
      kind: "quoted",
      quote: { orderId: "o1", totalCents: 5694 },
    });
  });
});
