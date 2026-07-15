from store import Order, OrderStore


def make_order(order_id="o1", status="CREATED"):
    return Order(
        order_id=order_id,
        customer="alice",
        items=["item-a"],
        amount=1000,
        status=status,
        created_at="2026-07-15T00:00:00",
        updated_at="2026-07-15T00:00:00",
    )


def test_create_adds_order_to_snapshot():
    store = OrderStore()
    store.create(make_order())

    snapshot = store.snapshot()

    assert len(snapshot) == 1
    assert snapshot[0]["order_id"] == "o1"
    assert snapshot[0]["status"] == "CREATED"


def test_snapshot_is_a_copy_not_a_live_reference():
    store = OrderStore()
    store.create(make_order())

    snapshot = store.snapshot()
    snapshot[0]["status"] = "TAMPERED"

    assert store.snapshot()[0]["status"] == "CREATED"


def test_update_status_changes_status_and_updated_at():
    store = OrderStore()
    store.create(make_order())

    store.update_status("o1", "PAID", updated_at="2026-07-15T01:00:00")

    order = store.snapshot()[0]
    assert order["status"] == "PAID"
    assert order["updated_at"] == "2026-07-15T01:00:00"


def test_update_status_raises_for_unknown_order():
    store = OrderStore()

    try:
        store.update_status("missing", "PAID", updated_at="2026-07-15T01:00:00")
        assert False, "expected KeyError"
    except KeyError:
        pass


def test_cancel_sets_status_cancelled_with_reason():
    store = OrderStore()
    store.create(make_order())

    store.cancel("o1", reason="out_of_stock", updated_at="2026-07-15T02:00:00")

    order = store.snapshot()[0]
    assert order["status"] == "CANCELLED"
    assert order["cancel_reason"] == "out_of_stock"
    assert order["updated_at"] == "2026-07-15T02:00:00"
