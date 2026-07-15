import json

import storage


def test_load_data_returns_empty_list_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))

    assert storage.load_data() == []


def test_save_then_load_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    original = [
        {"id": 1, "name": "홍길동", "email": "hong@example.com"},
        {"id": 2, "name": "김철수", "email": "kim@example.com"},
    ]

    storage.save_data(original)

    assert storage.load_data() == original


def test_save_data_preserves_korean_without_unicode_escape(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(data_file))

    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])

    content = data_file.read_text(encoding="utf-8")
    assert "홍길동" in content
    assert "\\u" not in content


def test_save_data_writes_indented_json(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(data_file))

    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])

    content = data_file.read_text(encoding="utf-8")
    assert "\n" in content
    assert '  "id"' in content


def test_save_empty_list(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(data_file))

    storage.save_data([])

    assert json.loads(data_file.read_text(encoding="utf-8")) == []
    assert storage.load_data() == []
