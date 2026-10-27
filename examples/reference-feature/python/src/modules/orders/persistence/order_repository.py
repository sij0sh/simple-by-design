from ..domain.order import Order
from ..domain.order_repository import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self, orders: tuple[Order, ...]) -> None:
        self._orders = orders

    def find_by_id(self, order_id: str) -> Order | None:
        return next((order for order in self._orders if order.id == order_id), None)
