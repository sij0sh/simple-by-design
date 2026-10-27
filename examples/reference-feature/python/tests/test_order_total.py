from modules.orders.api.quote_order import quote_order
from modules.orders.domain.order import Order, OrderLine
from modules.orders.domain.pricing import total_cents
from modules.orders.persistence.order_repository import InMemoryOrderRepository

ORDER = Order(
    id="o1",
    lines=(OrderLine(sku="a", unit_cents=6699, quantity=1),),
    discount_percent=15,
)


def test_total_applies_a_rounded_discount() -> None:
    assert total_cents(ORDER) == 5694


def test_quote_returns_the_total_for_a_stored_order() -> None:
    repo = InMemoryOrderRepository((ORDER,))
    assert quote_order(repo, "o1").total_cents == 5694
