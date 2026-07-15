import json

from dummygen.writer import write_json


def test_write_json_creates_file_with_records(tmp_path):
    records = [{"a": 1}, {"a": 2}]
    output_path = tmp_path / "out.json"

    write_json(records, str(output_path))

    with open(output_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded == records


def test_write_json_creates_parent_directories(tmp_path):
    records = [{"a": 1}]
    output_path = tmp_path / "nested" / "dir" / "out.json"

    write_json(records, str(output_path))

    assert output_path.exists()
