import pytest

from model.sample import Sample


def test_sample_생성_시_입력한_필드가_그대로_보존된다():
    sample = Sample(
        sample_id="SMP-001",
        name="Wafer-A",
        avg_production_time=2.5,
        yield_rate=0.9,
    )

    assert sample.sample_id == "SMP-001"
    assert sample.name == "Wafer-A"
    assert sample.avg_production_time == 2.5
    assert sample.yield_rate == 0.9


def test_sample_생성_시_초기_재고는_0이다():
    sample = Sample(
        sample_id="SMP-001",
        name="Wafer-A",
        avg_production_time=2.5,
        yield_rate=0.9,
    )

    assert sample.stock == 0


@pytest.mark.parametrize("yield_rate", [-0.1, 1.1, -1, 2])
def test_수율이_0에서_1_범위를_벗어나면_거부된다(yield_rate):
    with pytest.raises(ValueError):
        Sample(
            sample_id="SMP-001",
            name="Wafer-A",
            avg_production_time=2.5,
            yield_rate=yield_rate,
        )
