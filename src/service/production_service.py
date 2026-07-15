import math


def calculate_shortage(order_quantity, available_stock):
    return order_quantity - available_stock


def calculate_actual_production(shortage, yield_rate):
    return math.ceil(shortage / yield_rate)


def calculate_total_production_time(avg_production_time, actual_production):
    return avg_production_time * actual_production


class ProductionService:
    def __init__(self):
        self._queue = []
        self._status = {}

    def enqueue(self, order_id, actual_production=None, total_production_time=None, shortage=None):
        self._queue.append(order_id)
        self._status[order_id] = {
            "order_id": order_id,
            "actual_production": actual_production,
            "total_production_time": total_production_time,
            "shortage": shortage,
        }

    def list_queue(self):
        return list(self._queue)

    def current_status(self):
        if not self._queue:
            return None
        return self._status[self._queue[0]]

    def dequeue(self):
        order_id = self._queue.pop(0)
        del self._status[order_id]
        return order_id
