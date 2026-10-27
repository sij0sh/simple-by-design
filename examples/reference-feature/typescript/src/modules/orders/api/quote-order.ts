import type { OrderRepository } from "../domain/order-repository";
import { totalCents } from "../domain/pricing";

export interface Quote {
  readonly orderId: string;
  readonly totalCents: number;
}

export function quoteOrder(
  repo: OrderRepository,
  rawId: unknown,
): Quote {
  const id = parseId(rawId);
  const order = repo.findById(id);
  if (order === undefined) {
    throw new Error(`unknown order: ${id}`);
  }
  return { orderId: order.id, totalCents: totalCents(order) };
}

function parseId(raw: unknown): string {
  if (typeof raw !== "string" || raw.trim() === "") {
    throw new Error("order id must be a non-empty string");
  }
  return raw;
}
