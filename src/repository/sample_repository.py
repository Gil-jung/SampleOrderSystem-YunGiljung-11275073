class SampleRepository:
    def __init__(self):
        self._samples = {}

    def add(self, sample):
        if sample.sample_id in self._samples:
            raise ValueError(f"sample_id already exists: {sample.sample_id}")
        self._samples[sample.sample_id] = sample

    def get(self, sample_id):
        return self._samples[sample_id]
