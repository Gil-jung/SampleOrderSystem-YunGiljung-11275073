from service.production_service import calculate_shortage


def test_부족분은_주문_수량에서_가용_재고를_뺀_값이다():
    assert calculate_shortage(order_quantity=5, available_stock=2) == 3
