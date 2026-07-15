class MenuController:
    def __init__(self, sample_service, order_service, monitoring_service, production_service):
        self._sample_service = sample_service
        self._order_service = order_service
        self._monitoring_service = monitoring_service
        self._production_service = production_service

    def register_sample(self, sample_id, name, avg_production_time, yield_rate):
        self._sample_service.register(sample_id, name, avg_production_time, yield_rate)

    def list_samples(self):
        return [self._sample_to_dict(sample) for sample in self._sample_service.list_all()]

    def search_samples(self, name):
        return [self._sample_to_dict(sample) for sample in self._sample_service.search(name)]

    def reserve_order(self, sample_id, customer_name, quantity):
        return self._order_service.reserve(sample_id, customer_name, quantity)

    def list_reserved_orders(self):
        return [
            self._order_to_dict(order_id, order)
            for order_id, order in self._order_service.list_reserved_with_ids()
        ]

    def approve_order(self, order_id):
        self._order_service.approve(order_id)

    def reject_order(self, order_id):
        self._order_service.reject(order_id)

    def get_order_counts(self):
        counts = self._monitoring_service.count_by_status()
        return {status.name: count for status, count in counts.items()}

    def get_stock_statuses(self):
        return [
            {
                "sample_id": sample.sample_id,
                "stock": sample.stock,
                "status": self._monitoring_service.stock_status(sample.sample_id),
            }
            for sample in self._sample_service.list_all()
        ]

    def get_production_queue(self):
        return self._production_service.list_queue()

    def get_current_production_status(self):
        return self._production_service.current_status()

    @staticmethod
    def _sample_to_dict(sample):
        return {
            "sample_id": sample.sample_id,
            "name": sample.name,
            "stock": sample.stock,
        }

    @staticmethod
    def _order_to_dict(order_id, order):
        return {
            "order_id": order_id,
            "sample_id": order.sample_id,
            "customer_name": order.customer_name,
            "quantity": order.quantity,
            "status": order.status.name,
        }
