from model.order import OrderStatus


class ReleaseService:
    def __init__(self, order_repository):
        self._order_repository = order_repository

    def release(self, order_id):
        order = self._order_repository.get(order_id)
        order.transition_to(OrderStatus.RELEASE)
