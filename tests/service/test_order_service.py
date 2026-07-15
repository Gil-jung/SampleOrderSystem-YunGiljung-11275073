from model.order import OrderStatus
from repository.order_repository import OrderRepository
from service.order_service import OrderService


def test_주문_예약_생성_시_RESERVED_상태_주문이_저장된다():
    order_repository = OrderRepository()
    service = OrderService(order_repository)

    order_id = service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)

    stored = order_repository.get(order_id)
    assert stored.sample_id == "SMP-001"
    assert stored.customer_name == "홍길동"
    assert stored.quantity == 5
    assert stored.status == OrderStatus.RESERVED
