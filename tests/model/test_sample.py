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
