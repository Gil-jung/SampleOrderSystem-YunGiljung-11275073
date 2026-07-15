from model.order import Order, OrderStatus


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
