from dataclasses import dataclass

from ..domain.invoice_repository import InvoiceRepository
from ..domain.pricing import total_cents


@dataclass(frozen=True)
class InvoiceView:
    id: str
    total_cents: int


def get_invoice(repo: InvoiceRepository, raw_id: object) -> InvoiceView:
    invoice_id = _parse_id(raw_id)
    invoice = repo.find_by_id(invoice_id)
    if invoice is None:
        raise LookupError(f"unknown invoice: {invoice_id}")
    return InvoiceView(id=invoice.id, total_cents=total_cents(invoice))


def _parse_id(raw: object) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("id must be a non-empty string")
    return raw
