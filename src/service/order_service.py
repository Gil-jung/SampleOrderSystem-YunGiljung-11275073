from model.order import Order


class OrderService:
    def __init__(self, order_repository):
        self._order_repository = order_repository

    def reserve(self, sample_id, customer_name, quantity):
        order = Order(sample_id=sample_id, customer_name=customer_name, quantity=quantity)
        return self._order_repository.add(order)
