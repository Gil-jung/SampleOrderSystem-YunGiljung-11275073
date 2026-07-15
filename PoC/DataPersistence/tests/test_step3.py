import crud
import storage


def test_read_all_prints_message_when_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))

    crud.read_all()

    captured = capsys.readouterr()
    assert "데이터가 없습니다." in captured.out


def test_read_all_prints_all_items(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data(
        [
            {"id": 1, "name": "홍길동", "email": "hong@example.com"},
            {"id": 2, "name": "김철수", "email": "kim@example.com"},
        ]
    )

    crud.read_all()

    captured = capsys.readouterr()
    assert "홍길동" in captured.out
    assert "김철수" in captured.out


def test_read_one_finds_existing_id(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    monkeypatch.setattr("builtins.input", lambda _: "1")

    crud.read_one()

    captured = capsys.readouterr()
    assert "홍길동" in captured.out


def test_read_one_reports_when_id_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    monkeypatch.setattr("builtins.input", lambda _: "999")

    crud.read_one()

    captured = capsys.readouterr()
    assert "id=999 데이터를 찾을 수 없습니다." in captured.out


def test_read_one_handles_non_numeric_input_gracefully(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    monkeypatch.setattr("builtins.input", lambda _: "abc")

    crud.read_one()

    captured = capsys.readouterr()
    assert "id=abc 데이터를 찾을 수 없습니다." in captured.out
