class MenuController:
    def __init__(self, sample_service):
        self._sample_service = sample_service

    def register_sample(self, sample_id, name, avg_production_time, yield_rate):
        self._sample_service.register(sample_id, name, avg_production_time, yield_rate)

    def list_samples(self):
        return [self._to_dict(sample) for sample in self._sample_service.list_all()]

    def search_samples(self, name):
        return [self._to_dict(sample) for sample in self._sample_service.search(name)]

    @staticmethod
    def _to_dict(sample):
        return {
            "sample_id": sample.sample_id,
            "name": sample.name,
            "stock": sample.stock,
        }
