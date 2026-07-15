from model.order import OrderStatus

_MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.CONFIRMED,
    OrderStatus.PRODUCING,
    OrderStatus.RELEASE,
]


class MonitoringService:
    def __init__(self, order_repository, sample_repository):
        self._order_repository = order_repository
        self._sample_repository = sample_repository

    def count_by_status(self):
        counts = {status: 0 for status in _MONITORED_STATUSES}
        for order in self._order_repository.list():
            if order.status in counts:
                counts[order.status] += 1
        return counts

    def stock_status(self, sample_id):
        demand = sum(
            order.quantity
            for order in self._order_repository.list()
            if order.sample_id == sample_id and order.status == OrderStatus.CONFIRMED
        )
        stock = self._sample_repository.get(sample_id).stock

        if stock >= demand:
            return "여유"
        elif stock > 0:
            return "부족"
