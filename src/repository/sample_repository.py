class SampleRepository:
    def __init__(self):
        self._samples = {}

    def add(self, sample):
        self._samples[sample.sample_id] = sample

    def get(self, sample_id):
        return self._samples[sample_id]
