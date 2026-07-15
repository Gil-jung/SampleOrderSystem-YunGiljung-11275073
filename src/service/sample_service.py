from model.sample import Sample


class SampleService:
    def __init__(self, repository):
        self._repository = repository

    def register(self, sample_id, name, avg_production_time, yield_rate):
        sample = Sample(
            sample_id=sample_id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
        )
        self._repository.add(sample)
