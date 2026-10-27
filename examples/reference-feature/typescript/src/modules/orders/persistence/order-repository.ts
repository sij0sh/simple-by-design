import type { Order } from "../domain/order";
import type { OrderRepository } from "../domain/order-repository";

export class InMemoryOrderRepository implements OrderRepository {
  private readonly orders: readonly Order[];

  constructor(orders: readonly Order[]) {
    this.orders = orders;
  }

  findById(id: string): Order | undefined {
    return this.orders.find((order) => order.id === id);
  }
}
