from .order import Order


def subtotal_cents(order: Order) -> int:
    return sum(line.unit_cents * line.quantity for line in order.lines)


def discount_cents(order: Order) -> int:
    if not 0 <= order.discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    return int(subtotal_cents(order) * order.discount_percent / 100)


def total_cents(order: Order) -> int:
    return subtotal_cents(order) - discount_cents(order)
