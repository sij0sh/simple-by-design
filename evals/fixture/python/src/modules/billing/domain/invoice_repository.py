from typing import Protocol

from .invoice import Invoice


class InvoiceRepository(Protocol):
    def find_by_id(self, invoice_id: str) -> Invoice | None: ...
