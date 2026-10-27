export interface InvoiceLine {
  readonly sku: string;
  readonly unitCents: number;
  readonly quantity: number;
}

export interface Invoice {
  readonly id: string;
  readonly orderId: string;
  readonly lines: readonly InvoiceLine[];
  readonly discountPercent: number;
}
