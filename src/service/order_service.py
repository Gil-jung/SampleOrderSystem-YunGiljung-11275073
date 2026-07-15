from model.order import Order


class OrderService:
    def __init__(self, order_repository, sample_repository):
        self._order_repository = order_repository
        self._sample_repository = sample_repository

    def reserve(self, sample_id, customer_name, quantity):
        try:
            self._sample_repository.get(sample_id)
        except KeyError:
            raise ValueError(f"unknown sample_id: {sample_id}")

        order = Order(sample_id=sample_id, customer_name=customer_name, quantity=quantity)
        return self._order_repository.add(order)
