from model.order import OrderStatus
from model.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.monitoring_service import MonitoringService
from service.order_service import OrderService
from service.production_service import ProductionService


def test_상태별_주문_수를_집계한다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    sample_repository.get("SMP-001").stock = 10
    order_service = OrderService(order_repository, sample_repository, ProductionService())
    monitoring_service = MonitoringService(order_repository, sample_repository)

    order_service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=1)
    order_service.reserve(sample_id="SMP-001", customer_name="김철수", quantity=1)
    confirmed_id = order_service.reserve(sample_id="SMP-001", customer_name="이영희", quantity=1)
    order_service.approve(confirmed_id)  # 재고 충분 -> CONFIRMED

    counts = monitoring_service.count_by_status()

    assert counts[OrderStatus.RESERVED] == 2
    assert counts[OrderStatus.CONFIRMED] == 1
    assert counts[OrderStatus.PRODUCING] == 0
    assert counts[OrderStatus.RELEASE] == 0


def test_REJECTED_주문은_집계에서_제외된다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_service = OrderService(order_repository, sample_repository, ProductionService())
    monitoring_service = MonitoringService(order_repository, sample_repository)

    order_id = order_service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=1)
    order_service.reject(order_id)

    counts = monitoring_service.count_by_status()

    assert sum(counts.values()) == 0
    assert OrderStatus.REJECTED not in counts


def test_재고가_미출고_수요_이상이면_여유로_판정한다():
    order_repository = OrderRepository()
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    sample_repository.get("SMP-001").stock = 10
    order_service = OrderService(order_repository, sample_repository, ProductionService())
    monitoring_service = MonitoringService(order_repository, sample_repository)

    order_id = order_service.reserve(sample_id="SMP-001", customer_name="홍길동", quantity=5)
    order_service.approve(order_id)  # 재고 충분 -> CONFIRMED, stock 10 -> 5

    assert monitoring_service.stock_status("SMP-001") == "여유"
