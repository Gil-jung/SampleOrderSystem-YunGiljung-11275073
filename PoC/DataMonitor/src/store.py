import threading
from dataclasses import asdict, dataclass


@dataclass
class Order:
    order_id: str
    customer: str
    items: list
    amount: int
    status: str
    created_at: str
    updated_at: str
    cancel_reason: str = None


class OrderStore:
    def __init__(self):
        self._orders: dict[str, Order] = {}
        self._lock = threading.Lock()

    def create(self, order: Order) -> None:
        with self._lock:
            self._orders[order.order_id] = order

    def update_status(self, order_id: str, status: str, updated_at: str) -> None:
        with self._lock:
            order = self._orders[order_id]
            order.status = status
            order.updated_at = updated_at

    def cancel(self, order_id: str, reason: str, updated_at: str) -> None:
        with self._lock:
            order = self._orders[order_id]
            order.status = "CANCELLED"
            order.cancel_reason = reason
            order.updated_at = updated_at

    def snapshot(self) -> list:
        with self._lock:
            return [asdict(order) for order in self._orders.values()]
