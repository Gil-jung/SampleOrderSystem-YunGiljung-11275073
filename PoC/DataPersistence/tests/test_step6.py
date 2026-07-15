import main


def test_menu_1_calls_create_item(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "create_item", lambda: calls.append("create"))
    inputs = iter(["1", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    assert calls == ["create"]


def test_menu_2_calls_read_all(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "read_all", lambda: calls.append("read_all"))
    inputs = iter(["2", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    assert calls == ["read_all"]


def test_menu_3_calls_read_one(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "read_one", lambda: calls.append("read_one"))
    inputs = iter(["3", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    assert calls == ["read_one"]


def test_menu_4_calls_update_item(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "update_item", lambda: calls.append("update"))
    inputs = iter(["4", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    assert calls == ["update"]


def test_menu_5_calls_delete_item(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "delete_item", lambda: calls.append("delete"))
    inputs = iter(["5", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    assert calls == ["delete"]


def test_menu_6_exits_loop(monkeypatch, capsys):
    for name in ("create_item", "read_all", "read_one", "update_item", "delete_item"):
        monkeypatch.setattr(main, name, lambda: (_ for _ in ()).throw(AssertionError("should not be called")))
    monkeypatch.setattr("builtins.input", lambda _: "6")

    main.main()

    captured = capsys.readouterr()
    assert "종료합니다." in captured.out


def test_menu_invalid_choice_shows_message_and_continues(monkeypatch, capsys):
    inputs = iter(["9", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    captured = capsys.readouterr()
    assert "잘못된 입력입니다." in captured.out


def test_menu_processes_multiple_choices_in_sequence(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "create_item", lambda: calls.append("create"))
    monkeypatch.setattr(main, "read_all", lambda: calls.append("read_all"))
    inputs = iter(["1", "2", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    assert calls == ["create", "read_all"]
