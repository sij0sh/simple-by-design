"""Consumer contract tests: imports only the declared orders API."""
from unittest import TestCase

from modules.orders.api import Order, OrderLine, quote_order


class Orders:
    def find_by_id(self, order_id: str) -> Order | None:
        if order_id == "o1":
            return Order("o1", (OrderLine("a", 6699, 1),), 15)
        return None


def test_quote_via_public_contract() -> None:
    quote = quote_order(Orders(), "o1")
    assert quote is not None
    assert quote.order_id == "o1"
    assert quote.total_cents == 5694


def test_invalid_id() -> None:
    with TestCase().assertRaises(ValueError):
        quote_order(Orders(), " ")


def test_missing_order() -> None:
    assert quote_order(Orders(), "missing") is None


def test_repository_failure_propagates_unchanged() -> None:
    failure = RuntimeError("repository unavailable")

    class UnavailableOrders:
        def find_by_id(self, order_id: str) -> Order | None:
            raise failure

    with TestCase().assertRaises(RuntimeError) as caught:
        quote_order(UnavailableOrders(), "o1")
    assert caught.exception is failure
