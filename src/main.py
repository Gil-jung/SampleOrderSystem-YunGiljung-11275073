from controller.menu_controller import MenuController
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.monitoring_service import MonitoringService
from service.order_service import OrderService
from service.production_service import ProductionService
from service.release_service import ReleaseService
from service.sample_service import SampleService
from view.console_view import ConsoleView


def build_controller():
    sample_repository = SampleRepository()
    order_repository = OrderRepository()
    production_service = ProductionService()
    sample_service = SampleService(sample_repository)
    order_service = OrderService(order_repository, sample_repository, production_service)
    monitoring_service = MonitoringService(order_repository, sample_repository)
    release_service = ReleaseService(order_repository)
    return MenuController(
        sample_service, order_service, monitoring_service, production_service, release_service
    )


def handle_sample_menu(controller, view):
    while True:
        print(view.render_sample_menu())
        choice = input("선택: ").strip()

        if choice == "1":
            sample_id = input("시료 ID: ").strip()
            name = input("이름: ").strip()
            avg_production_time = float(input("평균 생산시간: ").strip())
            yield_rate = float(input("수율: ").strip())
            controller.register_sample(sample_id, name, avg_production_time, yield_rate)
            print("등록 완료")
        elif choice == "2":
            print(view.render_sample_list(controller.list_samples()))
        elif choice == "3":
            keyword = input("검색어: ").strip()
            print(view.render_sample_list(controller.search_samples(keyword)))
        elif choice == "0":
            break


def handle_order_menu(controller, view):
    while True:
        print(view.render_order_menu())
        choice = input("선택: ").strip()

        if choice == "1":
            sample_id = input("시료 ID: ").strip()
            customer_name = input("고객명: ").strip()
            quantity = int(input("수량: ").strip())
            order_id = controller.reserve_order(sample_id, customer_name, quantity)
            print(f"예약 완료: {order_id}")
        elif choice == "2":
            print(view.render_order_list(controller.list_reserved_orders()))
        elif choice == "3":
            order_id = input("주문 ID: ").strip()
            controller.approve_order(order_id)
            print("승인 완료")
        elif choice == "4":
            order_id = input("주문 ID: ").strip()
            controller.reject_order(order_id)
            print("거절 완료")
        elif choice == "0":
            break


def handle_monitoring_menu(controller, view):
    while True:
        print(view.render_monitoring_menu())
        choice = input("선택: ").strip()

        if choice == "1":
            print(view.render_order_counts(controller.get_order_counts()))
        elif choice == "2":
            print(view.render_stock_statuses(controller.get_stock_statuses()))
        elif choice == "0":
            break


def handle_release_menu(controller, view):
    while True:
        print(view.render_release_menu())
        choice = input("선택: ").strip()

        if choice == "1":
            print(view.render_order_list(controller.list_confirmed_orders()))
        elif choice == "2":
            order_id = input("주문 ID: ").strip()
            controller.release_order(order_id)
            print("출고 완료")
        elif choice == "0":
            break


def handle_production_menu(controller, view):
    while True:
        print(view.render_production_menu())
        choice = input("선택: ").strip()

        if choice == "1":
            print(view.render_current_production(controller.get_current_production_status()))
        elif choice == "2":
            print(view.render_production_queue(controller.get_production_queue()))
        elif choice == "3":
            controller.complete_current_production()
            print("생산 완료")
        elif choice == "0":
            break


def main():
    controller = build_controller()
    view = ConsoleView()

    while True:
        samples = controller.list_samples()
        summary = {
            "sample_count": len(samples),
            "total_stock": sum(sample["stock"] for sample in samples),
        }
        print(view.render_main_menu(summary))
        choice = input("선택: ").strip()

        if choice == "1":
            handle_sample_menu(controller, view)
        elif choice == "2":
            handle_order_menu(controller, view)
        elif choice == "3":
            handle_monitoring_menu(controller, view)
        elif choice == "4":
            handle_release_menu(controller, view)
        elif choice == "5":
            handle_production_menu(controller, view)
        elif choice == "0":
            print("종료합니다.")
            break


if __name__ == "__main__":
    main()
