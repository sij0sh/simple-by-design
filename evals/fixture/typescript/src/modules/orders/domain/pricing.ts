import type { Order } from "./order.ts";

export function subtotalCents(order: Order): number {
  return order.lines.reduce(
    (sum, line) => sum + line.unitCents * line.quantity,
    0,
  );
}

export function discountCents(order: Order): number {
  if (order.discountPercent < 0 || order.discountPercent > 100) {
    throw new Error("discountPercent must be between 0 and 100");
  }
  return Math.round((subtotalCents(order) * order.discountPercent) / 100);
}

export function totalCents(order: Order): number {
  return subtotalCents(order) - discountCents(order);
}
