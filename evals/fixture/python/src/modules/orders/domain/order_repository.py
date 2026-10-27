from typing import Protocol

from .order import Order


class OrderRepository(Protocol):
    def find_by_id(self, order_id: str) -> Order | None: ...
