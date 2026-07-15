import pytest

from model.order import Order, OrderError, OrderStatus


def test_order_생성_시_초기_상태는_RESERVED이다():
    order = Order(
        sample_id="SMP-001",
        customer_name="홍길동",
        quantity=10,
    )

    assert order.status == OrderStatus.RESERVED
    assert order.sample_id == "SMP-001"
    assert order.customer_name == "홍길동"
    assert order.quantity == 10


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_수량이_0_이하이면_거부된다(quantity):
    with pytest.raises(ValueError):
        Order(
            sample_id="SMP-001",
            customer_name="홍길동",
            quantity=quantity,
        )


def _make_order(status):
    order = Order(sample_id="SMP-001", customer_name="홍길동", quantity=1)
    order.status = status
    return order


@pytest.mark.parametrize(
    "from_status, to_status",
    [
        (OrderStatus.RESERVED, OrderStatus.CONFIRMED),
        (OrderStatus.RESERVED, OrderStatus.PRODUCING),
        (OrderStatus.RESERVED, OrderStatus.REJECTED),
        (OrderStatus.PRODUCING, OrderStatus.CONFIRMED),
        (OrderStatus.CONFIRMED, OrderStatus.RELEASE),
    ],
)
def test_허용된_상태_전이는_성공한다(from_status, to_status):
    order = _make_order(from_status)

    order.transition_to(to_status)

    assert order.status == to_status


@pytest.mark.parametrize(
    "from_status, to_status",
    [
        (OrderStatus.RESERVED, OrderStatus.RELEASE),
        (OrderStatus.CONFIRMED, OrderStatus.PRODUCING),
        (OrderStatus.CONFIRMED, OrderStatus.REJECTED),
        (OrderStatus.PRODUCING, OrderStatus.RESERVED),
        (OrderStatus.PRODUCING, OrderStatus.REJECTED),
        (OrderStatus.REJECTED, OrderStatus.CONFIRMED),
        (OrderStatus.REJECTED, OrderStatus.RELEASE),
        (OrderStatus.RELEASE, OrderStatus.CONFIRMED),
        (OrderStatus.RELEASE, OrderStatus.REJECTED),
    ],
)
def test_허용되지_않은_상태_전이는_OrderError로_거부된다(from_status, to_status):
    order = _make_order(from_status)

    with pytest.raises(OrderError):
        order.transition_to(to_status)

    assert order.status == from_status
