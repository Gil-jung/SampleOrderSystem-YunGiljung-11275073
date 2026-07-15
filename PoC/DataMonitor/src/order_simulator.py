from store import Order, OrderStore

CUSTOMERS = ["alice", "bob", "carol", "dave", "erin"]
ITEMS = ["keyboard", "mouse", "monitor", "headset", "webcam", "mousepad"]
CANCEL_REASONS = ["out_of_stock", "customer_request", "payment_failed"]

STATUS_FLOW = ["CREATED", "PAID", "SHIPPING", "DELIVERED"]
CANCEL_PROBABILITY = 0.2


def generate_order(order_id: str, now: str, rng) -> Order:
    items = rng.sample(ITEMS, k=rng.randint(1, 3))
    return Order(
        order_id=order_id,
        customer=rng.choice(CUSTOMERS),
        items=items,
        amount=rng.randint(1000, 100000),
        status="CREATED",
        created_at=now,
        updated_at=now,
    )


def run_scenario(store: OrderStore, count: int, rng, clock) -> None:
    for i in range(count):
        order_id = f"order-{i + 1}"
        order = generate_order(order_id, now=clock(), rng=rng)
        store.create(order)

        if rng.random() < CANCEL_PROBABILITY:
            store.cancel(order_id, reason=rng.choice(CANCEL_REASONS), updated_at=clock())
        else:
            for status in STATUS_FLOW[1:]:
                store.update_status(order_id, status, updated_at=clock())
