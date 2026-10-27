from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    sku: str
    unit_cents: int
    quantity: int


@dataclass(frozen=True)
class Order:
    id: str
    customer_id: str
    lines: tuple[OrderLine, ...]
    discount_percent: int
