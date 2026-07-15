from model.order import OrderStatus

_MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.CONFIRMED,
    OrderStatus.PRODUCING,
    OrderStatus.RELEASE,
]


class MonitoringService:
    def __init__(self, order_repository):
        self._order_repository = order_repository

    def count_by_status(self):
        counts = {status: 0 for status in _MONITORED_STATUSES}
        for order in self._order_repository.list():
            if order.status in counts:
                counts[order.status] += 1
        return counts
