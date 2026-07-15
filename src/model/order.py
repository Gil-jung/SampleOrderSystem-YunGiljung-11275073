from dataclasses import dataclass
from enum import Enum, auto


class OrderStatus(Enum):
    RESERVED = auto()
    REJECTED = auto()
    PRODUCING = auto()
    CONFIRMED = auto()
    RELEASE = auto()


class OrderError(Exception):
    pass


_ALLOWED_TRANSITIONS = {
    OrderStatus.RESERVED: {OrderStatus.CONFIRMED, OrderStatus.PRODUCING, OrderStatus.REJECTED},
    OrderStatus.PRODUCING: {OrderStatus.CONFIRMED},
    OrderStatus.CONFIRMED: {OrderStatus.RELEASE},
    OrderStatus.REJECTED: set(),
    OrderStatus.RELEASE: set(),
}


@dataclass
class Order:
    sample_id: str
    customer_name: str
    quantity: int
    status: OrderStatus = OrderStatus.RESERVED

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

    def transition_to(self, new_status):
        if new_status not in _ALLOWED_TRANSITIONS[self.status]:
            raise OrderError(f"cannot transition from {self.status} to {new_status}")
        self.status = new_status
