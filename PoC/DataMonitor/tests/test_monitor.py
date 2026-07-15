from monitor import apply_filter, apply_sort, diff_changed_ids, main_loop, parse_args, render, summarize


def orders():
    return [
        {"order_id": "o1", "status": "PAID", "amount": 100, "created_at": "2026-07-15T00:00:01"},
        {"order_id": "o2", "status": "CREATED", "amount": 200, "created_at": "2026-07-15T00:00:02"},
        {"order_id": "o3", "status": "PAID", "amount": 300, "created_at": "2026-07-15T00:00:00"},
    ]


def test_summarize_counts_total_and_by_status():
    summary = summarize(orders())

    assert summary["total"] == 3
    assert summary["by_status"]["PAID"] == 2
    assert summary["by_status"]["CREATED"] == 1


def test_summarize_empty_snapshot():
    summary = summarize([])

    assert summary["total"] == 0
    assert summary["by_status"] == {}


def test_apply_filter_matches_status():
    filtered = apply_filter(orders(), "status=PAID")

    assert {o["order_id"] for o in filtered} == {"o1", "o3"}


def test_apply_filter_none_returns_all():
    assert apply_filter(orders(), None) == orders()


def test_apply_sort_orders_by_key_ascending():
    sorted_orders = apply_sort(orders(), "created_at")

    assert [o["order_id"] for o in sorted_orders] == ["o3", "o1", "o2"]


def test_apply_sort_none_preserves_order():
    assert apply_sort(orders(), None) == orders()


def test_diff_changed_ids_detects_new_and_modified_orders():
    prev = [{"order_id": "o1", "status": "CREATED"}]
    current = [
        {"order_id": "o1", "status": "PAID"},
        {"order_id": "o2", "status": "CREATED"},
    ]

    changed = diff_changed_ids(prev, current)

    assert changed == {"o1", "o2"}


def test_diff_changed_ids_no_change_returns_empty_set():
    prev = [{"order_id": "o1", "status": "CREATED"}]
    current = [{"order_id": "o1", "status": "CREATED"}]

    assert diff_changed_ids(prev, current) == set()


def test_render_shows_empty_message_when_no_data():
    output = render([], changed_ids=set())

    assert "데이터 없음" in output


def test_render_shows_summary_and_rows():
    output = render(orders(), changed_ids=set())

    assert "총 3건" in output
    assert "PAID: 2" in output
    assert "CREATED: 1" in output
    assert "o1" in output
    assert "o2" in output
    assert "o3" in output


def test_render_highlights_changed_rows():
    output = render(orders(), changed_ids={"o2"})

    lines = {line.strip(): line for line in output.splitlines()}
    o1_line = next(line for line in output.splitlines() if "o1" in line)
    o2_line = next(line for line in output.splitlines() if "o2" in line)

    assert not o1_line.strip().startswith("*")
    assert o2_line.strip().startswith("*")


def test_parse_args_defaults():
    args = parse_args([])

    assert args.interval == 1.5
    assert args.filter is None
    assert args.sort is None


def test_parse_args_custom_options():
    args = parse_args(["--interval", "0.5", "--filter", "status=PAID", "--sort", "created_at"])

    assert args.interval == 0.5
    assert args.filter == "status=PAID"
    assert args.sort == "created_at"


class FakeStore:
    def __init__(self, snapshots):
        self._snapshots = iter(snapshots)

    def snapshot(self):
        return next(self._snapshots)


def test_main_loop_renders_each_snapshot_and_sleeps_between_polls():
    store = FakeStore([orders()[:1], orders()])
    outputs = []
    sleep_calls = []

    main_loop(
        store,
        interval=1.0,
        filter_expr=None,
        sort_key=None,
        sleep_fn=sleep_calls.append,
        output_fn=outputs.append,
        max_iterations=2,
    )

    assert len(outputs) == 2
    assert "o1" in outputs[0]
    assert "o2" in outputs[1] and "o3" in outputs[1]
    assert sleep_calls == [1.0, 1.0]


def test_main_loop_handles_store_errors_without_crashing():
    class FlakyStore:
        def __init__(self):
            self.calls = 0

        def snapshot(self):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("boom")
            return orders()

    outputs = []
    main_loop(
        FlakyStore(),
        interval=0.1,
        filter_expr=None,
        sort_key=None,
        sleep_fn=lambda _: None,
        output_fn=outputs.append,
        max_iterations=2,
    )

    assert any("오류" in output for output in outputs[:1])
    assert "o1" in outputs[1]
