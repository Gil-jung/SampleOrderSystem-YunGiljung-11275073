class OrderView:
    """Controller가 넘긴 순수 데이터(dict)를 문자열로 포맷팅만 한다. 비즈니스 로직 없음."""

    @staticmethod
    def render_order(order_data: dict) -> str:
        lines = [
            f"[주문번호 {order_data['order_id']}] 고객: {order_data['customer_name']} "
            f"| 상태: {order_data['status']}",
        ]
        if not order_data["items"]:
            lines.append("  (담긴 상품 없음)")
        for item in order_data["items"]:
            lines.append(
                f"  - {item['name']} x {item['quantity']} = {item['subtotal']:,}원"
            )
        lines.append(f"  합계: {order_data['total_price']:,}원")
        return "\n".join(lines)

    @staticmethod
    def render_order_list(orders_data: list[dict]) -> str:
        if not orders_data:
            return "등록된 주문이 없습니다."
        return "\n\n".join(OrderView.render_order(o) for o in orders_data)

    @staticmethod
    def render_error(message: str) -> str:
        return f"[오류] {message}"
