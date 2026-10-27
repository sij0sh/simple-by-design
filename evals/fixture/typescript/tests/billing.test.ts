import assert from "node:assert/strict";
import { test } from "node:test";
import { getInvoice } from "../src/modules/billing/api/billing-api.ts";
import type { Invoice } from "../src/modules/billing/domain/invoice.ts";
import { totalCents } from "../src/modules/billing/domain/pricing.ts";
import { InMemoryInvoiceRepository } from "../src/modules/billing/persistence/invoice-repository.ts";

const invoice: Invoice = {
  id: "i1",
  orderId: "o1",
  lines: [{ sku: "a", unitCents: 6699, quantity: 1 }],
  discountPercent: 15,
};

test("invoice total rounds a fractional discount", () => {
  assert.equal(totalCents(invoice), 5694);
});

test("getInvoice returns the stored invoice total", () => {
  const repo = new InMemoryInvoiceRepository([invoice]);
  assert.deepEqual(getInvoice(repo, "i1"), { id: "i1", totalCents: 5694 });
});
