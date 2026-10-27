import assert from "node:assert/strict";
import { test } from "node:test";
import { getOrder } from "../src/modules/orders/api/orders-api.ts";
import type { Order } from "../src/modules/orders/domain/order.ts";
import { totalCents } from "../src/modules/orders/domain/pricing.ts";
import { InMemoryOrderRepository } from "../src/modules/orders/persistence/order-repository.ts";

const order: Order = {
  id: "o1",
  customerId: "c1",
  lines: [{ sku: "a", unitCents: 6699, quantity: 1 }],
  discountPercent: 15,
};

test("order total rounds a fractional discount", () => {
  assert.equal(totalCents(order), 5694);
});

test("getOrder returns the stored order total", () => {
  const repo = new InMemoryOrderRepository([order]);
  assert.deepEqual(getOrder(repo, "o1"), { id: "o1", totalCents: 5694 });
});
