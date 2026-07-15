import argparse
import time


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="데이터 모니터링 Tool")
    parser.add_argument("--interval", type=float, default=1.5, help="polling 주기(초)")
    parser.add_argument("--filter", type=str, default=None, help="예: status=PAID")
    parser.add_argument("--sort", type=str, default=None, help="정렬 기준 필드명")
    return parser.parse_args(argv)


def summarize(snapshot: list) -> dict:
    by_status: dict = {}
    for order in snapshot:
        by_status[order["status"]] = by_status.get(order["status"], 0) + 1
    return {"total": len(snapshot), "by_status": by_status}


def apply_filter(snapshot: list, filter_expr: str) -> list:
    if not filter_expr:
        return snapshot
    key, _, value = filter_expr.partition("=")
    return [order for order in snapshot if str(order.get(key)) == value]


def apply_sort(snapshot: list, sort_key: str) -> list:
    if not sort_key:
        return snapshot
    return sorted(snapshot, key=lambda order: order.get(sort_key))


def diff_changed_ids(prev_snapshot: list, snapshot: list) -> set:
    prev_by_id = {order["order_id"]: order for order in prev_snapshot}
    changed = set()
    for order in snapshot:
        order_id = order["order_id"]
        if order_id not in prev_by_id or prev_by_id[order_id] != order:
            changed.add(order_id)
    return changed


def render(snapshot: list, changed_ids: set) -> str:
    if not snapshot:
        return "데이터 없음"

    summary = summarize(snapshot)
    lines = [f"총 {summary['total']}건"]
    lines.append(" | ".join(f"{status}: {count}" for status, count in summary["by_status"].items()))
    lines.append("-" * 40)

    for order in snapshot:
        marker = "* " if order["order_id"] in changed_ids else "  "
        lines.append(
            f"{marker}{order['order_id']:<10} {order['status']:<10} {order.get('customer', ''):<10} {order.get('amount', '')}"
        )

    return "\n".join(lines)


def main_loop(store, interval, filter_expr, sort_key, sleep_fn, output_fn, max_iterations=None):
    prev_snapshot = []
    iterations = 0

    while max_iterations is None or iterations < max_iterations:
        try:
            snapshot = store.snapshot()
            changed_ids = diff_changed_ids(prev_snapshot, snapshot)
            view = apply_sort(apply_filter(snapshot, filter_expr), sort_key)
            output_fn(render(view, changed_ids))
            prev_snapshot = snapshot
        except Exception as exc:
            output_fn(f"[오류] 데이터 조회 실패: {exc}")

        sleep_fn(interval)
        iterations += 1


def main(argv=None):
    from order_simulator import run_scenario
    from store import OrderStore
    import random

    args = parse_args(argv)
    store = OrderStore()
    run_scenario(store, count=20, rng=random.Random(), clock=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))

    def clear_and_print(text: str) -> None:
        print("\033[2J\033[H", end="")
        print(text)

    main_loop(
        store,
        interval=args.interval,
        filter_expr=args.filter,
        sort_key=args.sort,
        sleep_fn=time.sleep,
        output_fn=clear_and_print,
    )


if __name__ == "__main__":
    main()
