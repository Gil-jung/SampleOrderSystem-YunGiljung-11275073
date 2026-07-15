import json

from dummygen.cli import main


def _write_schema(tmp_path):
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "x-generator": {"pattern": "ID-{seq:03d}"}},
            "amount": {"type": "integer", "x-generator": {"min": 1, "max": 100}},
        },
    }
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema), encoding="utf-8")
    return schema_file


def test_generate_command_writes_output_file(tmp_path):
    schema_file = _write_schema(tmp_path)
    output_file = tmp_path / "out.json"

    exit_code = main([
        "generate",
        "--schema", str(schema_file),
        "--count", "5",
        "--output", str(output_file),
        "--seed", "1",
    ])

    assert exit_code == 0
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(data) == 5
    assert data[0]["id"] == "ID-000"


def test_generate_command_returns_nonzero_for_missing_schema(tmp_path, capsys):
    output_file = tmp_path / "out.json"

    exit_code = main([
        "generate",
        "--schema", str(tmp_path / "missing.json"),
        "--count", "1",
        "--output", str(output_file),
    ])

    assert exit_code != 0
