from model.order import Order, OrderError, OrderStatus
from model.product import Product


class OrderController:
    """주문 유스케이스를 조율한다. Model만 알고 View는 알지 못한다."""

    def __init__(self):
        self._orders: dict[str, Order] = {}
        self._next_id: int = 1

    def create_order(self, customer_name: str) -> str:
        if not customer_name.strip():
            raise OrderError("고객명은 비어 있을 수 없습니다.")
        order_id = f"ORD-{self._next_id:04d}"
        self._next_id += 1
        self._orders[order_id] = Order(order_id=order_id, customer_name=customer_name)
        return order_id

    def add_item(self, order_id: str, product: Product, quantity: int) -> None:
        self._get_order(order_id).add_item(product, quantity)

    def remove_item(self, order_id: str, product_id: str) -> None:
        self._get_order(order_id).remove_item(product_id)

    def change_status(self, order_id: str, new_status: OrderStatus) -> None:
        self._get_order(order_id).change_status(new_status)

    def cancel_order(self, order_id: str) -> None:
        self._get_order(order_id).change_status(OrderStatus.CANCELLED)

    def get_order_data(self, order_id: str) -> dict:
        order = self._get_order(order_id)
        return {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "status": order.status.value,
            "items": [
                {
                    "product_id": i.product.product_id,
                    "name": i.product.name,
                    "price": i.product.price,
                    "quantity": i.quantity,
                    "subtotal": i.subtotal,
                }
                for i in order.items
            ],
            "total_price": order.total_price(),
        }

    def list_orders_data(self) -> list[dict]:
        return [self.get_order_data(oid) for oid in self._orders]

    def _get_order(self, order_id: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderError(f"존재하지 않는 주문번호입니다: {order_id}")
        return order
