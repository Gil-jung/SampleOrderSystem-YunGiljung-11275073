from dataclasses import dataclass, field
from enum import Enum

from model.product import Product


class OrderStatus(Enum):
    CREATED = "주문생성"
    PAID = "결제완료"
    SHIPPED = "배송중"
    COMPLETED = "배송완료"
    CANCELLED = "주문취소"


# 상태 전이 규칙: key 상태에서 value 집합의 상태로만 전이 가능
_ALLOWED_TRANSITIONS = {
    OrderStatus.CREATED: {OrderStatus.PAID, OrderStatus.CANCELLED},
    OrderStatus.PAID: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


@dataclass
class OrderItem:
    product: Product
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError(f"수량은 1개 이상이어야 합니다: {self.quantity}")

    @property
    def subtotal(self) -> int:
        return self.product.price * self.quantity


class OrderError(Exception):
    """주문 도메인 규칙 위반 시 발생하는 예외"""


@dataclass
class Order:
    order_id: str
    customer_name: str
    items: list[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.CREATED

    def add_item(self, product: Product, quantity: int) -> None:
        if self.status != OrderStatus.CREATED:
            raise OrderError(
                f"'{self.status.value}' 상태의 주문에는 상품을 추가할 수 없습니다."
            )
        for item in self.items:
            if item.product.product_id == product.product_id:
                item.quantity += quantity
                return
        self.items.append(OrderItem(product, quantity))

    def remove_item(self, product_id: str) -> None:
        if self.status != OrderStatus.CREATED:
            raise OrderError(
                f"'{self.status.value}' 상태의 주문에서는 상품을 제거할 수 없습니다."
            )
        before = len(self.items)
        self.items = [i for i in self.items if i.product.product_id != product_id]
        if len(self.items) == before:
            raise OrderError(f"주문에 존재하지 않는 상품입니다: {product_id}")

    def total_price(self) -> int:
        return sum(item.subtotal for item in self.items)

    def change_status(self, new_status: OrderStatus) -> None:
        if self.status == new_status:
            raise OrderError(f"이미 '{new_status.value}' 상태입니다.")
        allowed = _ALLOWED_TRANSITIONS[self.status]
        if new_status not in allowed:
            raise OrderError(
                f"'{self.status.value}' 상태에서 '{new_status.value}' 상태로 전이할 수 없습니다."
            )
        if new_status == OrderStatus.PAID and not self.items:
            raise OrderError("주문에 상품이 없어 결제를 진행할 수 없습니다.")
        self.status = new_status
