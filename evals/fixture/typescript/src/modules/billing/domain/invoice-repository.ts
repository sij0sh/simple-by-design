import type { Invoice } from "./invoice.ts";

export interface InvoiceRepository {
  findById(id: string): Invoice | undefined;
}
