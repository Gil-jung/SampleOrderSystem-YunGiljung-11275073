from view.order_view import OrderView


def test_주문_데이터를_보기_좋게_렌더링한다():
    order_data = {
        "order_id": "ORD-0001",
        "customer_name": "홍길동",
        "status": "주문생성",
        "items": [
            {"product_id": "P001", "name": "아메리카노", "price": 4500, "quantity": 2, "subtotal": 9000},
        ],
        "total_price": 9000,
    }

    rendered = OrderView.render_order(order_data)

    assert "ORD-0001" in rendered
    assert "홍길동" in rendered
    assert "아메리카노" in rendered
    assert "9,000원" in rendered


def test_상품이_없는_주문은_안내_문구를_포함한다():
    order_data = {
        "order_id": "ORD-0001",
        "customer_name": "홍길동",
        "status": "주문생성",
        "items": [],
        "total_price": 0,
    }

    rendered = OrderView.render_order(order_data)

    assert "담긴 상품 없음" in rendered


def test_빈_주문_목록은_안내_문구를_반환한다():
    assert OrderView.render_order_list([]) == "등록된 주문이 없습니다."


def test_오류_메시지는_오류_접두어와_함께_렌더링된다():
    rendered = OrderView.render_error("존재하지 않는 주문번호입니다: ORD-9999")
    assert rendered == "[오류] 존재하지 않는 주문번호입니다: ORD-9999"
