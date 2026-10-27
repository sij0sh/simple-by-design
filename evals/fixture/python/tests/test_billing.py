from modules.billing.api.billing_api import get_invoice
from modules.billing.domain.invoice import Invoice, InvoiceLine
from modules.billing.domain.pricing import total_cents
from modules.billing.persistence.invoice_repository import InMemoryInvoiceRepository

INVOICE = Invoice(
    id="i1",
    order_id="o1",
    lines=(InvoiceLine(sku="a", unit_cents=6699, quantity=1),),
    discount_percent=15,
)


def test_invoice_total_rounds_a_fractional_discount() -> None:
    assert total_cents(INVOICE) == 5694


def test_get_invoice_returns_the_stored_total() -> None:
    repo = InMemoryInvoiceRepository((INVOICE,))
    assert get_invoice(repo, "i1").total_cents == 5694
