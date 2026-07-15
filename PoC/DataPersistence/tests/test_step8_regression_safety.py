import os
import subprocess
import sys
from pathlib import Path

import crud
import main
import storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------------


def test_create_item_id_never_duplicates_across_delete_create_cycles(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    assigned_ids = []

    def create(name, email):
        inputs = iter([name, email])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        crud.create_item()

    def delete(target_id):
        inputs = iter([str(target_id), "y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        crud.delete_item()

    create("홍길동", "hong@example.com")  # id=1
    create("김철수", "kim@example.com")  # id=2
    create("이순신", "lee@example.com")  # id=3
    assigned_ids += [item["id"] for item in storage.load_data()]

    delete(2)  # 남은: 1, 3
    create("박영희", "park@example.com")  # id=4
    assigned_ids.append(storage.load_data()[-1]["id"])

    delete(1)  # 남은: 3, 4
    create("최민수", "choi@example.com")  # id=5
    assigned_ids.append(storage.load_data()[-1]["id"])

    assert assigned_ids == [1, 2, 3, 4, 5]
    assert len(set(assigned_ids)) == len(assigned_ids)


def test_main_survives_multiple_consecutive_invalid_choices(monkeypatch, capsys):
    inputs = iter(["9", "x", "", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    captured = capsys.readouterr()
    assert captured.out.count("잘못된 입력입니다.") == 3
    assert "종료합니다." in captured.out


def test_main_process_survives_full_scenario_via_real_subprocess(tmp_path):
    env = dict(os.environ, PYTHONUTF8="1")
    scenario_input = (
        "2\n"
        "1\n홍길동\nhong@example.com\n"
        "1\n김철수\nkim@example.com\n"
        "2\n"
        "3\n1\n"
        "4\n1\n\nnew@example.com\n"
        "3\n1\n"
        "5\n2\nn\n"
        "5\n2\ny\n"
        "2\n"
        "6\n"
    )

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        input=scenario_input,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 0
    assert result.stderr == ""


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------


def test_delete_item_requires_exact_lowercase_y_to_confirm(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    original = [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]
    storage.save_data(original)

    for bogus_confirm in ["yes", "n", "", "ㅇ"]:
        inputs = iter(["1", bogus_confirm])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        crud.delete_item()

    assert storage.load_data() == original


def test_id_lookup_tolerates_surrounding_whitespace(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])

    monkeypatch.setattr("builtins.input", lambda _: " 1 ")
    crud.read_one()
    captured = capsys.readouterr()
    assert "홍길동" in captured.out

    inputs = iter([" 1 ", "박영희", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    crud.update_item()
    assert storage.load_data() == [{"id": 1, "name": "박영희", "email": "hong@example.com"}]


def test_update_and_delete_do_not_write_file_when_target_not_found(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(data_file))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    mtime_before = data_file.stat().st_mtime_ns

    monkeypatch.setattr("builtins.input", lambda _: "999")
    crud.update_item()
    assert data_file.stat().st_mtime_ns == mtime_before

    monkeypatch.setattr("builtins.input", lambda _: "999")
    crud.delete_item()
    assert data_file.stat().st_mtime_ns == mtime_before


def test_special_characters_survive_round_trip_without_corruption(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    tricky_name = '김"철수 😀'
    tricky_email = "weird+chars\\@example.com"
    inputs = iter([tricky_name, tricky_email])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.create_item()

    data = storage.load_data()
    assert data == [{"id": 1, "name": tricky_name, "email": tricky_email}]

    crud.read_all()
    captured = capsys.readouterr()
    # print(dict)의 repr은 backslash를 이스케이프하므로, name(backslash 미포함) 존재 여부로 확인한다.
    assert tricky_name in captured.out


def test_every_record_always_has_exactly_id_name_email_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))

    def create(name, email):
        inputs = iter([name, email])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        crud.create_item()

    def update(target_id, name, email):
        inputs = iter([str(target_id), name, email])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        crud.update_item()

    def delete(target_id):
        inputs = iter([str(target_id), "y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        crud.delete_item()

    create("홍길동", "hong@example.com")
    create("김철수", "kim@example.com")
    update(1, "", "new@example.com")
    delete(2)
    create("이순신", "lee@example.com")

    for item in storage.load_data():
        assert set(item.keys()) == {"id", "name", "email"}


def test_delete_removes_exactly_one_matching_record(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data(
        [
            {"id": 1, "name": "중복", "email": "dup@example.com"},
            {"id": 1, "name": "중복", "email": "dup@example.com"},
            {"id": 2, "name": "김철수", "email": "kim@example.com"},
        ]
    )

    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.delete_item()

    data = storage.load_data()
    assert len(data) == 2
    assert sum(1 for item in data if item["id"] == 1) == 1
    assert sum(1 for item in data if item["id"] == 2) == 1
