import crud
import storage


def test_update_item_reports_when_id_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    monkeypatch.setattr("builtins.input", lambda _: "999")

    crud.update_item()

    captured = capsys.readouterr()
    assert "id=999 데이터를 찾을 수 없습니다." in captured.out
    assert storage.load_data() == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]


def test_update_item_updates_both_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "박영희", "park@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.update_item()

    data = storage.load_data()
    assert data == [{"id": 1, "name": "박영희", "email": "park@example.com"}]


def test_update_item_keeps_existing_value_when_input_blank(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "박영희", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.update_item()

    data = storage.load_data()
    assert data == [{"id": 1, "name": "박영희", "email": "hong@example.com"}]


def test_update_item_persists_to_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "", "new@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.update_item()

    reloaded = storage.load_data()
    assert reloaded[0]["email"] == "new@example.com"


def test_update_item_does_not_affect_other_records(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data(
        [
            {"id": 1, "name": "홍길동", "email": "hong@example.com"},
            {"id": 2, "name": "김철수", "email": "kim@example.com"},
        ]
    )
    inputs = iter(["1", "박영희", "park@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.update_item()

    data = storage.load_data()
    assert data[1] == {"id": 2, "name": "김철수", "email": "kim@example.com"}
