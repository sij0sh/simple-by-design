import type { Order } from "./order";

export interface OrderRepository {
  findById(id: string): Order | undefined;
}
