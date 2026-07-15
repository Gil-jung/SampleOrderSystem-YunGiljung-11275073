class OrderRepository:
    def __init__(self):
        self._orders = {}
        self._next_id = 1

    def add(self, order):
        order_id = f"ORD-{self._next_id:04d}"
        self._next_id += 1
        self._orders[order_id] = order
        return order_id

    def get(self, order_id):
        return self._orders[order_id]
