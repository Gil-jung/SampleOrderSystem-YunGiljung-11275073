from repository.sample_repository import SampleRepository
from service.sample_service import SampleService
from controller.menu_controller import MenuController


def test_시료_등록_명령이_SampleService로_위임된다():
    repository = SampleRepository()
    sample_service = SampleService(repository)
    controller = MenuController(sample_service)

    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )

    stored = repository.get("SMP-001")
    assert stored.name == "Wafer-A"
    assert stored.stock == 0


def test_시료_목록_조회_명령이_dict_리스트로_반환된다():
    repository = SampleRepository()
    sample_service = SampleService(repository)
    controller = MenuController(sample_service)
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )

    result = controller.list_samples()

    assert result == [{"sample_id": "SMP-001", "name": "Wafer-A", "stock": 0}]


def test_시료_검색_명령이_dict_리스트로_반환된다():
    repository = SampleRepository()
    sample_service = SampleService(repository)
    controller = MenuController(sample_service)
    controller.register_sample(
        sample_id="SMP-001", name="Wafer-A", avg_production_time=2.5, yield_rate=0.9
    )
    controller.register_sample(
        sample_id="SMP-002", name="Other-B", avg_production_time=1.0, yield_rate=0.8
    )

    result = controller.search_samples("Wafer")

    assert result == [{"sample_id": "SMP-001", "name": "Wafer-A", "stock": 0}]
