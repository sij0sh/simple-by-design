import type { Invoice } from "./invoice.ts";

export function subtotalCents(invoice: Invoice): number {
  return invoice.lines.reduce(
    (sum, line) => sum + line.unitCents * line.quantity,
    0,
  );
}

export function discountCents(invoice: Invoice): number {
  if (invoice.discountPercent < 0 || invoice.discountPercent > 100) {
    throw new Error("discountPercent must be between 0 and 100");
  }
  return Math.round((subtotalCents(invoice) * invoice.discountPercent) / 100);
}

export function totalCents(invoice: Invoice): number {
  return subtotalCents(invoice) - discountCents(invoice);
}
