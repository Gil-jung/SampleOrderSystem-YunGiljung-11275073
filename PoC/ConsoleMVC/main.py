from controller.order_controller import OrderController
from model.order import OrderError, OrderStatus
from model.product import Product
from view.order_view import OrderView


def run_demo() -> None:
    controller = OrderController()
    view = OrderView()

    americano = Product("P001", "아메리카노", 4500)
    latte = Product("P002", "카페라떼", 5000)

    order_id = controller.create_order("홍길동")
    controller.add_item(order_id, americano, 2)
    controller.add_item(order_id, latte, 1)

    print(view.render_order(controller.get_order_data(order_id)))

    controller.change_status(order_id, OrderStatus.PAID)
    controller.change_status(order_id, OrderStatus.SHIPPED)
    controller.change_status(order_id, OrderStatus.COMPLETED)

    print(view.render_order(controller.get_order_data(order_id)))

    try:
        controller.change_status(order_id, OrderStatus.CANCELLED)
    except OrderError as e:
        print(view.render_error(str(e)))


if __name__ == "__main__":
    run_demo()
