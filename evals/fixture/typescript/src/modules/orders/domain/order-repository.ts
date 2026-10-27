import type { Order } from "./order.ts";

export interface OrderRepository {
  findById(id: string): Order | undefined;
}
