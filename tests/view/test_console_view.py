from view.console_view import ConsoleView


def test_메인_메뉴는_5개_항목과_시료_요약_정보를_표시한다():
    view = ConsoleView()

    output = view.render_main_menu({"sample_count": 3, "total_stock": 42})

    assert "시료 관리" in output
    assert "주문" in output
    assert "모니터링" in output
    assert "출고 처리" in output
    assert "생산 라인" in output
    assert "3" in output
    assert "42" in output


def test_메인_메뉴에_종료_항목이_표시된다():
    view = ConsoleView()

    output = view.render_main_menu({"sample_count": 0, "total_stock": 0})

    assert "0. 종료" in output
