import type { InvoiceRepository } from "../domain/invoice-repository.ts";
import { totalCents } from "../domain/pricing.ts";

export interface InvoiceView {
  readonly id: string;
  readonly totalCents: number;
}

export function getInvoice(
  repo: InvoiceRepository,
  rawId: unknown,
): InvoiceView {
  const id = parseId(rawId);
  const invoice = repo.findById(id);
  if (invoice === undefined) {
    throw new Error(`unknown invoice: ${id}`);
  }
  return { id: invoice.id, totalCents: totalCents(invoice) };
}

function parseId(raw: unknown): string {
  if (typeof raw !== "string" || raw.trim() === "") {
    throw new Error("id must be a non-empty string");
  }
  return raw;
}
