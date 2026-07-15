import pytest

from controller.order_controller import OrderController
from model.order import OrderError, OrderStatus
from model.product import Product
from view.order_view import OrderView


@pytest.fixture
def controller():
    return OrderController()


@pytest.fixture
def products():
    return {
        "americano": Product("P001", "아메리카노", 4500),
        "latte": Product("P002", "카페라떼", 5000),
    }


def test_주문_생성_및_상품_추가_후_합계_계산(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 2)
    controller.add_item(order_id, products["latte"], 1)

    data = controller.get_order_data(order_id)

    assert data["customer_name"] == "홍길동"
    assert data["status"] == OrderStatus.CREATED.value
    assert data["total_price"] == 4500 * 2 + 5000


def test_동일_상품_추가시_수량이_누적된다(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 1)
    controller.add_item(order_id, products["americano"], 2)

    data = controller.get_order_data(order_id)

    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 3


def test_상품_제거(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 1)
    controller.add_item(order_id, products["latte"], 1)

    controller.remove_item(order_id, "P001")

    data = controller.get_order_data(order_id)
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "P002"


def test_정상적인_상태_전이_흐름(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 1)

    controller.change_status(order_id, OrderStatus.PAID)
    controller.change_status(order_id, OrderStatus.SHIPPED)
    controller.change_status(order_id, OrderStatus.COMPLETED)

    assert controller.get_order_data(order_id)["status"] == OrderStatus.COMPLETED.value


def test_주문_취소(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 1)

    controller.cancel_order(order_id)

    assert controller.get_order_data(order_id)["status"] == OrderStatus.CANCELLED.value


def test_완료된_주문은_취소할_수_없다(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 1)
    controller.change_status(order_id, OrderStatus.PAID)
    controller.change_status(order_id, OrderStatus.SHIPPED)
    controller.change_status(order_id, OrderStatus.COMPLETED)

    with pytest.raises(OrderError):
        controller.cancel_order(order_id)


def test_상품이_없는_주문은_결제할_수_없다(controller):
    order_id = controller.create_order("홍길동")

    with pytest.raises(OrderError):
        controller.change_status(order_id, OrderStatus.PAID)


def test_취소된_주문에는_상품을_추가할_수_없다(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 1)
    controller.cancel_order(order_id)

    with pytest.raises(OrderError):
        controller.add_item(order_id, products["latte"], 1)


def test_잘못된_상태_전이는_거부된다(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 1)

    with pytest.raises(OrderError):
        controller.change_status(order_id, OrderStatus.SHIPPED)


def test_존재하지_않는_주문_조회시_예외(controller):
    with pytest.raises(OrderError):
        controller.get_order_data("ORD-9999")


def test_음수_또는_0_수량은_거부된다(controller, products):
    order_id = controller.create_order("홍길동")
    with pytest.raises(ValueError):
        controller.add_item(order_id, products["americano"], 0)


def test_view는_controller가_준_데이터만으로_렌더링한다(controller, products):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, products["americano"], 2)

    rendered = OrderView.render_order(controller.get_order_data(order_id))

    assert "아메리카노" in rendered
    assert "9,000원" in rendered
    assert order_id in rendered


def test_주문_목록_렌더링(controller, products):
    o1 = controller.create_order("홍길동")
    o2 = controller.create_order("김철수")
    controller.add_item(o1, products["americano"], 1)
    controller.add_item(o2, products["latte"], 1)

    rendered = OrderView.render_order_list(controller.list_orders_data())

    assert "홍길동" in rendered and "김철수" in rendered
