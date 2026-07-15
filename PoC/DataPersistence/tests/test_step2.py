import crud
import storage


def test_create_item_assigns_id_1_when_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    inputs = iter(["홍길동", "hong@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.create_item()

    data = storage.load_data()
    assert data == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]


def test_create_item_increments_id_sequentially(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    inputs = iter(["홍길동", "hong@example.com", "김철수", "kim@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.create_item()
    crud.create_item()

    data = storage.load_data()
    assert [item["id"] for item in data] == [1, 2]


def test_create_item_does_not_reuse_deleted_id(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(data_file))
    # id=1,2,3 중 중간 번호(2)가 삭제되어 결번이 생긴 상태를 가정
    storage.save_data(
        [
            {"id": 1, "name": "홍길동", "email": "hong@example.com"},
            {"id": 3, "name": "이순신", "email": "lee@example.com"},
        ]
    )

    inputs = iter(["박영희", "park@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.create_item()

    data = storage.load_data()
    assert [item["id"] for item in data] == [1, 3, 4]


def test_create_item_saves_stripped_input(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    inputs = iter(["  홍길동  ", "  hong@example.com  "])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.create_item()

    data = storage.load_data()
    assert data == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]


def test_create_item_persists_to_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    inputs = iter(["홍길동", "hong@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.create_item()

    reloaded = storage.load_data()
    assert len(reloaded) == 1
    assert reloaded[0]["name"] == "홍길동"
