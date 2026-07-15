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

    def enqueue(self, order_id):
        self._queue.append(order_id)

    def list_queue(self):
        return list(self._queue)
