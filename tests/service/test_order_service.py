import pytest

from model.order import OrderStatus
from model.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.order_service import OrderService


def test_주문_예약_생성_시_RESERVED_상태_주문이_저장된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    service = OrderService(order_repository, sample_repository)

    order_id = service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)

    stored = order_repository.get(order_id)
    assert stored.sample_id == "SMP-001"
    assert stored.customer_name == "홍길동"
    assert stored.quantity == 5
    assert stored.status == OrderStatus.RESERVED


def test_존재하지_않는_시료로_예약하면_거부된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    service = OrderService(order_repository, sample_repository)

    with pytest.raises(ValueError):
        service.reserve(sample_id="UNKNOWN", customer_name="홍길동", quantity=5)


def test_등록된_시료여도_수량이_0_이하이면_예약이_거부된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    service = OrderService(order_repository, sample_repository)

    with pytest.raises(ValueError):
        service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=0)
