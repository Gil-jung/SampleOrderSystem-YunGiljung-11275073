import crud
import storage


def test_delete_item_reports_when_id_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    monkeypatch.setattr("builtins.input", lambda _: "999")

    crud.delete_item()

    captured = capsys.readouterr()
    assert "id=999 데이터를 찾을 수 없습니다." in captured.out
    assert storage.load_data() == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]


def test_delete_item_cancels_when_not_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.delete_item()

    captured = capsys.readouterr()
    assert "삭제가 취소되었습니다." in captured.out
    assert storage.load_data() == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]


def test_delete_item_removes_when_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.delete_item()

    captured = capsys.readouterr()
    assert "[삭제 완료] id=1" in captured.out
    assert storage.load_data() == []


def test_delete_item_confirmation_is_case_insensitive(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "Y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.delete_item()

    assert storage.load_data() == []


def test_delete_item_does_not_affect_other_records(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data(
        [
            {"id": 1, "name": "홍길동", "email": "hong@example.com"},
            {"id": 2, "name": "김철수", "email": "kim@example.com"},
        ]
    )
    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.delete_item()

    data = storage.load_data()
    assert data == [{"id": 2, "name": "김철수", "email": "kim@example.com"}]


def test_delete_item_persists_removal_to_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data(
        [
            {"id": 1, "name": "홍길동", "email": "hong@example.com"},
            {"id": 2, "name": "김철수", "email": "kim@example.com"},
        ]
    )
    inputs = iter(["2", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.delete_item()

    reloaded = storage.load_data()
    assert [item["id"] for item in reloaded] == [1]
