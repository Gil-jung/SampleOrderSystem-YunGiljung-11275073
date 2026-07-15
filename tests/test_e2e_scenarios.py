from model.order import OrderStatus
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.monitoring_service import MonitoringService
from service.order_service import OrderService
from service.production_service import ProductionService
from service.release_service import ReleaseService
from service.sample_service import SampleService
from controller.menu_controller import MenuController


def _build_controller():
    sample_repository = SampleRepository()
    order_repository = OrderRepository()
    production_service = ProductionService()
    sample_service = SampleService(sample_repository)
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    release_service = ReleaseService(order_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service, release_service
    )
    return controller, sample_repository, order_repository, order_service


def test_재고_충분_시나리오_등록부터_출고까지_끊김없이_동작한다():
    controller, sample_repository, order_repository, _ = _build_controller()
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )
    sample_repository.get("SMP-001").stock = 10  # 재고 임의 확보

    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=5
    )
    controller.approve_order(order_id)
    controller.release_order(order_id)

    released_order = order_repository.get(order_id)
    assert released_order.status == OrderStatus.RELEASE
    assert sample_repository.get("SMP-001").stock == 5


def test_재고_부족_시나리오_생산_완료를_거쳐_출고까지_끊김없이_동작한다():
    controller, sample_repository, order_repository, order_service = _build_controller()
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )
    # 재고는 등록 직후 기본값 0

    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=9
    )
    controller.approve_order(order_id)  # 재고 부족 -> PRODUCING, 큐 등록

    assert order_repository.get(order_id).status == OrderStatus.PRODUCING
    assert controller.get_production_queue() == [order_id]

    order_service.complete_production()  # 생산 완료 -> CONFIRMED

    assert order_repository.get(order_id).status == OrderStatus.CONFIRMED
    assert controller.get_production_queue() == []

    controller.release_order(order_id)

    released_order = order_repository.get(order_id)
    assert released_order.status == OrderStatus.RELEASE
    assert sample_repository.get("SMP-001").stock == 0


def test_거절_시나리오_예약_후_거절하면_모니터링_집계에서_제외된다():
    controller, sample_repository, order_repository, order_service = _build_controller()
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )

    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=1
    )
    controller.reject_order(order_id)

    assert order_repository.get(order_id).status == OrderStatus.REJECTED
    counts = controller.get_order_counts()
    assert sum(counts.values()) == 0


def test_FIFO_다중_생산_시나리오_등록_순서대로_생산_완료된다():
    controller, sample_repository, order_repository, order_service = _build_controller()
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )
    # 재고는 등록 직후 기본값 0

    first_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=9
    )
    second_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="김철수", quantity=5
    )
    controller.approve_order(first_id)
    controller.approve_order(second_id)

    assert controller.get_production_queue() == [first_id, second_id]

    order_service.complete_production()  # first_id 완료

    assert order_repository.get(first_id).status == OrderStatus.CONFIRMED
    assert order_repository.get(second_id).status == OrderStatus.PRODUCING
    assert controller.get_production_queue() == [second_id]

    order_service.complete_production()  # second_id 완료

    assert order_repository.get(second_id).status == OrderStatus.CONFIRMED
    assert controller.get_production_queue() == []
