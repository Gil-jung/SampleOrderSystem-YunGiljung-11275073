import pytest

from model.order import OrderError, OrderStatus
from model.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.order_service import OrderService
from service.production_service import ProductionService
from service.release_service import ReleaseService


def test_CONFIRMED_주문을_출고하면_RELEASE로_전환된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    sample_repository.get("SMP-001").stock = 10
    order_service = OrderService(order_repository, sample_repository, ProductionService())
    release_service = ReleaseService(order_repository)

    order_id = order_service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)
    order_service.approve(order_id)  # 재고 충분 -> CONFIRMED

    release_service.release(order_id)

    released_order = order_repository.get(order_id)
    assert released_order.status == OrderStatus.RELEASE


def test_CONFIRMED가_아닌_주문을_출고하면_OrderError로_거부된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_service = OrderService(order_repository, sample_repository, ProductionService())
    release_service = ReleaseService(order_repository)

    order_id = order_service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=1)
    # 아직 RESERVED 상태 (승인 전)

    with pytest.raises(OrderError):
        release_service.release(order_id)
