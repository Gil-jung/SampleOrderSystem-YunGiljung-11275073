import pytest

from model.order import Order, OrderError, OrderItem, OrderStatus
from model.product import Product


@pytest.fixture
def americano():
    return Product("P001", "아메리카노", 4500)


@pytest.fixture
def latte():
    return Product("P002", "카페라떼", 5000)


def test_주문_생성시_기본_상태는_주문생성이다():
    order = Order("ORD-0001", "홍길동")
    assert order.status == OrderStatus.CREATED
    assert order.items == []


def test_상품_추가시_합계가_계산된다(americano, latte):
    order = Order("ORD-0001", "홍길동")
    order.add_item(americano, 2)
    order.add_item(latte, 1)
    assert order.total_price() == 4500 * 2 + 5000


def test_동일_상품_추가시_수량이_누적된다(americano):
    order = Order("ORD-0001", "홍길동")
    order.add_item(americano, 1)
    order.add_item(americano, 2)
    assert len(order.items) == 1
    assert order.items[0].quantity == 3


def test_주문항목_수량은_1개_미만일_수_없다(americano):
    with pytest.raises(ValueError):
        OrderItem(americano, 0)


def test_주문생성_상태가_아니면_상품_추가가_거부된다(americano):
    order = Order("ORD-0001", "홍길동")
    order.add_item(americano, 1)
    order.change_status(OrderStatus.PAID)

    with pytest.raises(OrderError):
        order.add_item(americano, 1)


def test_정의되지_않은_상태_전이는_거부된다():
    order = Order("ORD-0001", "홍길동")
    with pytest.raises(OrderError):
        order.change_status(OrderStatus.SHIPPED)


def test_상품이_없으면_결제로_전이할_수_없다():
    order = Order("ORD-0001", "홍길동")
    with pytest.raises(OrderError):
        order.change_status(OrderStatus.PAID)


def test_완료_또는_취소_상태는_더_이상_전이할_수_없다(americano):
    order = Order("ORD-0001", "홍길동")
    order.add_item(americano, 1)
    order.change_status(OrderStatus.PAID)
    order.change_status(OrderStatus.SHIPPED)
    order.change_status(OrderStatus.COMPLETED)

    with pytest.raises(OrderError):
        order.change_status(OrderStatus.CANCELLED)
