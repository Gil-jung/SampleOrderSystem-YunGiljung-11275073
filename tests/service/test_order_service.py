import pytest

from model.order import Order, OrderStatus
from model.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.order_service import OrderService
from service.production_service import ProductionService


def test_주문_예약_생성_시_RESERVED_상태_주문이_저장된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    service = OrderService(order_repository, sample_repository, ProductionService())

    order_id = service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)

    stored = order_repository.get(order_id)
    assert stored.sample_id == "SMP-001"
    assert stored.customer_name == "홍길동"
    assert stored.quantity == 5
    assert stored.status == OrderStatus.RESERVED


def test_존재하지_않는_시료로_예약하면_거부된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    service = OrderService(order_repository, sample_repository, ProductionService())

    with pytest.raises(ValueError):
        service.reserve(sample_id="UNKNOWN", customer_name="홍길동", quantity=5)


def test_등록된_시료여도_수량이_0_이하이면_예약이_거부된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    service = OrderService(order_repository, sample_repository, ProductionService())

    with pytest.raises(ValueError):
        service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=0)


def test_접수된_주문_목록_조회_시_RESERVED_상태만_반환된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    service = OrderService(order_repository, sample_repository, ProductionService())

    service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)

    rejected_order = Order(sample_id="SMP-001", customer_name="김철수", quantity=3)
    rejected_order.transition_to(OrderStatus.REJECTED)
    order_repository.add(rejected_order)

    reserved_orders = service.list_reserved()

    assert len(reserved_orders) == 1
    assert reserved_orders[0].customer_name == "홍길동"
    assert reserved_orders[0].status == OrderStatus.RESERVED


def test_재고가_충분하면_승인_시_즉시_CONFIRMED로_전환되고_재고가_차감된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    sample_repository.get("SMP-001").stock = 10
    service = OrderService(order_repository, sample_repository, ProductionService())
    order_id = service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)

    service.approve(order_id)

    approved_order = order_repository.get(order_id)
    assert approved_order.status == OrderStatus.CONFIRMED
    assert sample_repository.get("SMP-001").stock == 5


def test_재고가_부족하면_승인_시_생산_큐에_등록되고_PRODUCING으로_전환된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    sample_repository.get("SMP-001").stock = 2
    production_service = ProductionService()
    service = OrderService(order_repository, sample_repository, production_service)
    order_id = service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)

    service.approve(order_id)

    approved_order = order_repository.get(order_id)
    assert approved_order.status == OrderStatus.PRODUCING
    assert order_id in production_service.list_queue()
