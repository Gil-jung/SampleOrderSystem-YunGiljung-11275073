import pytest

from controller.order_controller import OrderController
from model.order import OrderError, OrderStatus
from model.product import Product


@pytest.fixture
def controller():
    return OrderController()


@pytest.fixture
def americano():
    return Product("P001", "아메리카노", 4500)


def test_주문_생성시_순번_기반_id가_발급된다(controller):
    order_id = controller.create_order("홍길동")
    assert order_id == "ORD-0001"


def test_빈_고객명으로는_주문을_생성할_수_없다(controller):
    with pytest.raises(OrderError):
        controller.create_order("   ")


def test_상품_추가_후_get_order_data는_dict를_반환한다(controller, americano):
    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, americano, 2)

    data = controller.get_order_data(order_id)

    assert isinstance(data, dict)
    assert data["total_price"] == 9000
    assert data["status"] == OrderStatus.CREATED.value


def test_존재하지_않는_주문_조회시_예외가_발생한다(controller):
    with pytest.raises(OrderError):
        controller.get_order_data("ORD-9999")


def test_존재하지_않는_주문에_상품_추가시_예외가_발생한다(controller, americano):
    with pytest.raises(OrderError):
        controller.add_item("ORD-9999", americano, 1)


def test_여러_주문_목록을_조회할_수_있다(controller, americano):
    o1 = controller.create_order("홍길동")
    o2 = controller.create_order("김철수")
    controller.add_item(o1, americano, 1)

    data_list = controller.list_orders_data()

    assert len(data_list) == 2
    assert {d["order_id"] for d in data_list} == {o1, o2}
