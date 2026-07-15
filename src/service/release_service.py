from model.order import OrderStatus


class ReleaseService:
    def __init__(self, order_repository):
        self._order_repository = order_repository

    def release(self, order_id):
        try:
            order = self._order_repository.get(order_id)
        except KeyError:
            raise ValueError(f"unknown order_id: {order_id}")

        order.transition_to(OrderStatus.RELEASE)
