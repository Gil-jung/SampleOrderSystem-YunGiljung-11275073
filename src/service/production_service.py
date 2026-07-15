class ProductionService:
    def __init__(self):
        self._queue = []

    def enqueue(self, order_id):
        self._queue.append(order_id)

    def list_queue(self):
        return list(self._queue)
