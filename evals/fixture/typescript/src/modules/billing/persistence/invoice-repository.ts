import type { Invoice } from "../domain/invoice.ts";
import type { InvoiceRepository } from "../domain/invoice-repository.ts";

export class InMemoryInvoiceRepository implements InvoiceRepository {
  private readonly invoices: readonly Invoice[];

  constructor(invoices: readonly Invoice[]) {
    this.invoices = invoices;
  }

  findById(id: string): Invoice | undefined {
    return this.invoices.find((invoice) => invoice.id === id);
  }
}
