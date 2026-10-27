from ..domain.invoice import Invoice
from ..domain.invoice_repository import InvoiceRepository


class InMemoryInvoiceRepository(InvoiceRepository):
    def __init__(self, invoices: tuple[Invoice, ...]) -> None:
        self._invoices = invoices

    def find_by_id(self, invoice_id: str) -> Invoice | None:
        return next(
            (invoice for invoice in self._invoices if invoice.id == invoice_id),
            None,
        )
