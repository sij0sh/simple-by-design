from .invoice import Invoice


def subtotal_cents(invoice: Invoice) -> int:
    return sum(line.unit_cents * line.quantity for line in invoice.lines)


def discount_cents(invoice: Invoice) -> int:
    if not 0 <= invoice.discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    return round(subtotal_cents(invoice) * invoice.discount_percent / 100)


def total_cents(invoice: Invoice) -> int:
    return subtotal_cents(invoice) - discount_cents(invoice)
