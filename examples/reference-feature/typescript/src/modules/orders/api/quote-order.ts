import type { OrderRepository } from "../domain/order-repository";
import { totalCents } from "../domain/pricing";

export interface Quote {
  readonly orderId: string;
  readonly totalCents: number;
}

export type QuoteResult =
  | { readonly kind: "quoted"; readonly quote: Quote }
  | { readonly kind: "not-found" };

export function quoteOrder(
  repo: OrderRepository,
  rawId: unknown,
): QuoteResult {
  const id = parseId(rawId);
  const order = repo.findById(id);
  if (order === undefined) {
    return { kind: "not-found" };
  }
  return { kind: "quoted", quote: { orderId: order.id, totalCents: totalCents(order) } };
}

function parseId(raw: unknown): string {
  if (typeof raw !== "string" || raw.trim() === "") {
    throw new Error("order id must be a non-empty string");
  }
  return raw;
}

// Public contract types; consumers need not import domain implementation paths.
export type { Order, OrderLine } from "../domain/order";
export type { OrderRepository } from "../domain/order-repository";
