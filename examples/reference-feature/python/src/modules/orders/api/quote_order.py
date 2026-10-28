from dataclasses import dataclass

from ..domain.order_repository import OrderRepository
from ..domain.pricing import total_cents


@dataclass(frozen=True)
class Quote:
    order_id: str
    total_cents: int


def quote_order(repo: OrderRepository, raw_id: object) -> Quote | None:
    order_id = _parse_id(raw_id)
    order = repo.find_by_id(order_id)
    if order is None:
        return None
    return Quote(order_id=order.id, total_cents=total_cents(order))


def _parse_id(raw: object) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("order id must be a non-empty string")
    return raw
