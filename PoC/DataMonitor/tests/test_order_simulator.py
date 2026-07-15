import itertools
import random

from order_simulator import generate_order, run_scenario
from store import OrderStore


def make_clock():
    counter = itertools.count(1)
    return lambda: f"2026-07-15T00:00:{next(counter):02d}"


def test_generate_order_has_created_status_and_valid_fields():
    rng = random.Random(42)
    order = generate_order("order-1", now="2026-07-15T00:00:00", rng=rng)

    assert order.order_id == "order-1"
    assert order.status == "CREATED"
    assert order.customer
    assert len(order.items) >= 1
    assert order.amount > 0


def test_run_scenario_creates_requested_number_of_orders():
    store = OrderStore()
    rng = random.Random(1)
    clock = make_clock()

    run_scenario(store, count=10, rng=rng, clock=clock)

    assert len(store.snapshot()) == 10


def test_run_scenario_orders_end_in_terminal_status():
    store = OrderStore()
    rng = random.Random(2)
    clock = make_clock()

    run_scenario(store, count=20, rng=rng, clock=clock)

    for order in store.snapshot():
        assert order["status"] in ("DELIVERED", "CANCELLED")
        if order["status"] == "CANCELLED":
            assert order["cancel_reason"]
