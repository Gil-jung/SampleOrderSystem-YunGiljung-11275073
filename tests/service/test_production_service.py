import pytest

from service.production_service import calculate_actual_production, calculate_shortage


def test_부족분은_주문_수량에서_가용_재고를_뺀_값이다():
    assert calculate_shortage(order_quantity=5, available_stock=2) == 3


@pytest.mark.parametrize(
    "shortage, yield_rate, expected",
    [
        (9, 0.9, 10),   # 나누어떨어지는 경우: 9 / 0.9 = 10.0 -> ceil = 10
        (5, 0.9, 6),    # 나누어떨어지지 않는 경우: 5 / 0.9 = 5.555... -> ceil = 6
    ],
)
def test_실_생산량은_부족분을_수율로_나눈_값을_올림한다(shortage, yield_rate, expected):
    assert calculate_actual_production(shortage, yield_rate) == expected
