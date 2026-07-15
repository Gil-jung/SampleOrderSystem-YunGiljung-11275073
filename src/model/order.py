from dataclasses import dataclass
from enum import Enum, auto


class OrderStatus(Enum):
    RESERVED = auto()


@dataclass
class Order:
    sample_id: str
    customer_name: str
    quantity: int
    status: OrderStatus = OrderStatus.RESERVED
