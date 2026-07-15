import itertools
import threading

from monitor import apply_filter, apply_sort, diff_changed_ids, render
from store import Order, OrderStore


def make_clock():
    counter = itertools.count(1)
    return lambda: f"2026-07-15T00:00:{next(counter):02d}"


def make_order(order_id, status="CREATED", created_at="2026-07-15T00:00:00"):
    return Order(
        order_id=order_id,
        customer="alice",
        items=["item-a"],
        amount=1000,
        status=status,
        created_at=created_at,
        updated_at=created_at,
    )


def test_s1_new_order_is_visible_and_marked_changed_in_next_poll():
    store = OrderStore()
    prev_snapshot = store.snapshot()

    store.create(make_order("o1"))
    snapshot = store.snapshot()

    changed = diff_changed_ids(prev_snapshot, snapshot)
    assert changed == {"o1"}
    assert "o1" in render(snapshot, changed)


def test_s2_status_transition_is_reflected_and_flagged_as_changed():
    store = OrderStore()
    store.create(make_order("o1"))
    baseline = store.snapshot()

    store.update_status("o1", "PAID", updated_at="2026-07-15T00:00:01")
    snapshot = store.snapshot()

    assert snapshot[0]["status"] == "PAID"
    assert diff_changed_ids(baseline, snapshot) == {"o1"}


def test_s3_cancel_records_status_and_reason_in_output():
    store = OrderStore()
    store.create(make_order("o1"))

    store.cancel("o1", reason="customer_request", updated_at="2026-07-15T00:00:01")
    snapshot = store.snapshot()

    assert snapshot[0]["status"] == "CANCELLED"
    assert snapshot[0]["cancel_reason"] == "customer_request"


def test_s4_bulk_creation_reports_exact_count_without_loss():
    store = OrderStore()
    clock = make_clock()

    for i in range(1000):
        store.create(make_order(f"order-{i}", created_at=clock()))

    snapshot = store.snapshot()
    assert len(snapshot) == 1000
    assert len({o["order_id"] for o in snapshot}) == 1000


def test_s5_concurrent_reads_during_writes_raise_no_exception():
    store = OrderStore()
    for i in range(50):
        store.create(make_order(f"order-{i}"))

    errors = []
    stop = threading.Event()

    def writer():
        i = 0
        while not stop.is_set():
            store.update_status(f"order-{i % 50}", "PAID", updated_at=f"t{i}")
            i += 1

    def reader():
        while not stop.is_set():
            try:
                store.snapshot()
            except Exception as exc:  # pragma: no cover - failure path
                errors.append(exc)

    threads = [threading.Thread(target=writer), threading.Thread(target=reader)]
    for t in threads:
        t.start()
    stop.wait(0.5)
    stop.set()
    for t in threads:
        t.join(timeout=2)

    assert errors == []
    assert len(store.snapshot()) == 50


def test_s6_filter_and_sort_combine_correctly():
    store = OrderStore()
    store.create(make_order("o1", status="PAID", created_at="2026-07-15T00:00:02"))
    store.create(make_order("o2", status="CREATED", created_at="2026-07-15T00:00:01"))
    store.create(make_order("o3", status="PAID", created_at="2026-07-15T00:00:00"))

    view = apply_sort(apply_filter(store.snapshot(), "status=PAID"), "created_at")

    assert [o["order_id"] for o in view] == ["o3", "o1"]


def test_s7_empty_store_renders_no_data_message():
    store = OrderStore()

    output = render(store.snapshot(), changed_ids=set())

    assert "데이터 없음" in output


def test_s8_many_poll_iterations_stay_stable():
    from monitor import main_loop

    store = OrderStore()
    store.create(make_order("o1"))
    outputs = []

    main_loop(
        store,
        interval=0,
        filter_expr=None,
        sort_key=None,
        sleep_fn=lambda _: None,
        output_fn=outputs.append,
        max_iterations=500,
    )

    assert len(outputs) == 500
    assert all("데이터 없음" not in output for output in outputs)
