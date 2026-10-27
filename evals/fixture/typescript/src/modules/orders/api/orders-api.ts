import type { OrderRepository } from "../domain/order-repository.ts";
import { totalCents } from "../domain/pricing.ts";

export interface OrderView {
  readonly id: string;
  readonly totalCents: number;
}

export function getOrder(repo: OrderRepository, rawId: unknown): OrderView {
  const id = parseId(rawId);
  const order = repo.findById(id);
  if (order === undefined) {
    throw new Error(`unknown order: ${id}`);
  }
  return { id: order.id, totalCents: totalCents(order) };
}

function parseId(raw: unknown): string {
  if (typeof raw !== "string" || raw.trim() === "") {
    throw new Error("id must be a non-empty string");
  }
  return raw;
}
