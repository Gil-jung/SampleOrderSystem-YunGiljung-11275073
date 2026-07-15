from model.order import OrderStatus
from model.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.monitoring_service import MonitoringService
from service.order_service import OrderService
from service.production_service import ProductionService
from service.sample_service import SampleService
from controller.menu_controller import MenuController


def test_시료_등록_명령이_SampleService로_위임된다():
    repository = SampleRepository()
    order_repository = OrderRepository()
    sample_service = SampleService(repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, repository, production_service)
    monitoring_service = MonitoringService(order_repository, repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )

    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )

    stored = repository.get("SMP-001")
    assert stored.name == "Wafer-A"
    assert stored.stock == 0


def test_시료_목록_조회_명령이_dict_리스트로_반환된다():
    repository = SampleRepository()
    order_repository = OrderRepository()
    sample_service = SampleService(repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, repository, production_service)
    monitoring_service = MonitoringService(order_repository, repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )

    result = controller.list_samples()

    assert result == [{"sample_id": "SMP-001", "name": "Wafer-A", "stock": 0}]


def test_시료_검색_명령이_dict_리스트로_반환된다():
    repository = SampleRepository()
    order_repository = OrderRepository()
    sample_service = SampleService(repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, repository, production_service)
    monitoring_service = MonitoringService(order_repository, repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )
    controller.register_sample(
        sample_id="SMP-002", name="Other-B", avg_production_time=1.0, yield_rate=0.8
    )

    result = controller.search_samples("Wafer")

    assert result == [{"sample_id": "SMP-001", "name": "Wafer-A", "stock": 0}]


def test_주문_예약_명령이_OrderService로_위임된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_repository = OrderRepository()
    sample_service = SampleService(sample_repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )

    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=5
    )

    stored = order_repository.get(order_id)
    assert stored.customer_name == "홍길동"
    assert stored.status == OrderStatus.RESERVED


def test_접수된_주문_목록_조회_명령이_dict_리스트로_반환된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_repository = OrderRepository()
    sample_service = SampleService(sample_repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=5
    )

    result = controller.list_reserved_orders()

    assert result == [
        {
            "order_id": order_id,
            "sample_id": "SMP-001",
            "customer_name": "홍길동",
            "quantity": 5,
            "status": "RESERVED",
        }
    ]


def test_주문_승인_명령이_OrderService로_위임된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    sample_repository.get("SMP-001").stock = 10
    order_repository = OrderRepository()
    sample_service = SampleService(sample_repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=5
    )

    controller.approve_order(order_id)

    assert order_repository.get(order_id).status == OrderStatus.CONFIRMED


def test_주문_거절_명령이_OrderService로_위임된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_repository = OrderRepository()
    sample_service = SampleService(sample_repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=5
    )

    controller.reject_order(order_id)

    assert order_repository.get(order_id).status == OrderStatus.REJECTED


def test_주문량_조회_명령이_상태명_키의_dict로_반환된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_repository = OrderRepository()
    sample_service = SampleService(sample_repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    controller.reserve_order(sample_id="SMP-001", customer_name="홍길동", quantity=1)

    result = controller.get_order_counts()

    assert result["RESERVED"] == 1
    assert result["CONFIRMED"] == 0
    assert result["PRODUCING"] == 0
    assert result["RELEASE"] == 0


def test_재고량_조회_명령이_시료별_재고_상태_리스트로_반환된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_repository = OrderRepository()
    sample_service = SampleService(sample_repository)
    production_service = ProductionService()
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )

    result = controller.get_stock_statuses()

    assert result == [{"sample_id": "SMP-001", "stock": 0, "status": "여유"}]


def test_생산_대기_큐_조회_명령이_ProductionService로_위임된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_repository = OrderRepository()
    production_service = ProductionService()
    sample_service = SampleService(sample_repository)
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=5
    )
    controller.approve_order(order_id)  # 재고 부족(0) -> PRODUCING, 큐에 등록

    result = controller.get_production_queue()

    assert result == [order_id]


def test_생산_현황_조회_명령이_ProductionService로_위임된다():
    sample_repository = SampleRepository()
    sample_repository.add(
        Sample(sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9)
    )
    order_repository = OrderRepository()
    production_service = ProductionService()
    sample_service = SampleService(sample_repository)
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    controller = MenuController(
        sample_service, order_service, monitoring_service, production_service
    )
    order_id = controller.reserve_order(
        sample_id="SMP-001", customer_name="홍길동", quantity=9
    )
    controller.approve_order(order_id)  # 재고 부족(0) -> PRODUCING

    result = controller.get_current_production_status()

    assert result["order_id"] == order_id
    assert result["actual_production"] == 10  # ceil(9/0.9) = 10
