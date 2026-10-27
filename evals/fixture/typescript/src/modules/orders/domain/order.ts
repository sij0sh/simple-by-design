export interface OrderLine {
  readonly sku: string;
  readonly unitCents: number;
  readonly quantity: number;
}

export interface Order {
  readonly id: string;
  readonly customerId: string;
  readonly lines: readonly OrderLine[];
  readonly discountPercent: number;
}
