from modules.orders.api.orders_api import get_order
from modules.orders.domain.order import Order, OrderLine
from modules.orders.domain.pricing import total_cents
from modules.orders.persistence.order_repository import InMemoryOrderRepository

ORDER = Order(
    id="o1",
    customer_id="c1",
    lines=(OrderLine(sku="a", unit_cents=6699, quantity=1),),
    discount_percent=15,
)


def test_order_total_rounds_a_fractional_discount() -> None:
    assert total_cents(ORDER) == 5694


def test_get_order_returns_the_stored_total() -> None:
    repo = InMemoryOrderRepository((ORDER,))
    assert get_order(repo, "o1").total_cents == 5694
