from model.order import Order, OrderStatus
from service.production_service import (
    calculate_actual_production,
    calculate_shortage,
    calculate_total_production_time,
)


class OrderService:
    def __init__(self, order_repository, sample_repository, production_service):
        self._order_repository = order_repository
        self._sample_repository = sample_repository
        self._production_service = production_service

    def reserve(self, sample_id, customer_name, quantity):
        try:
            self._sample_repository.get(sample_id)
        except KeyError:
            raise ValueError(f"unknown sample_id: {sample_id}")

        order = Order(sample_id=sample_id, customer_name=customer_name, quantity=quantity)
        return self._order_repository.add(order)

    def list_reserved(self):
        return [
            order
            for order in self._order_repository.list()
            if order.status == OrderStatus.RESERVED
        ]

    def approve(self, order_id):
        try:
            order = self._order_repository.get(order_id)
        except KeyError:
            raise ValueError(f"unknown order_id: {order_id}")

        sample = self._sample_repository.get(order.sample_id)

        if sample.stock >= order.quantity:
            sample.stock -= order.quantity
            order.transition_to(OrderStatus.CONFIRMED)
        else:
            shortage = calculate_shortage(order.quantity, sample.stock)
            actual_production = calculate_actual_production(shortage, sample.yield_rate)
            total_production_time = calculate_total_production_time(
                sample.avg_production_time, actual_production
            )
            order.transition_to(OrderStatus.PRODUCING)
            self._production_service.enqueue(
                order_id, actual_production, total_production_time, shortage
            )

    def reject(self, order_id):
        order = self._order_repository.get(order_id)
        order.transition_to(OrderStatus.REJECTED)

    def complete_production(self):
        status = self._production_service.current_status()
        order = self._order_repository.get(status["order_id"])
        sample = self._sample_repository.get(order.sample_id)

        sample.stock += status["shortage"]
        sample.stock -= order.quantity
        order.transition_to(OrderStatus.CONFIRMED)
        self._production_service.dequeue()
