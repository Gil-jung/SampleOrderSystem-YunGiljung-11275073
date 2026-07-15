import pytest

from repository.sample_repository import SampleRepository
from service.sample_service import SampleService


def test_시료_등록_시_초기_재고_0으로_저장된다():
    repository = SampleRepository()
    service = SampleService(repository)

    service.register(
        sample_id="SMP-001",
        name="Wafer-A",
        avg_production_time=2.5,
        yield_rate=0.9,
    )

    stored = repository.get("SMP-001")
    assert stored.sample_id == "SMP-001"
    assert stored.name == "Wafer-A"
    assert stored.avg_production_time == 2.5
    assert stored.yield_rate == 0.9
    assert stored.stock == 0


def test_이미_존재하는_시료_ID로_등록하면_거부된다():
    repository = SampleRepository()
    service = SampleService(repository)
    service.register(
        sample_id="SMP-001",
        name="Wafer-A",
        avg_production_time=2.5,
        yield_rate=0.9,
    )

    with pytest.raises(ValueError):
        service.register(
            sample_id="SMP-001",
            name="Wafer-B",
            avg_production_time=1.0,
            yield_rate=0.8,
        )
