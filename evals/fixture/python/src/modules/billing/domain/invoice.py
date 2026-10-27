from dataclasses import dataclass


@dataclass(frozen=True)
class InvoiceLine:
    sku: str
    unit_cents: int
    quantity: int


@dataclass(frozen=True)
class Invoice:
    id: str
    order_id: str
    lines: tuple[InvoiceLine, ...]
    discount_percent: int
