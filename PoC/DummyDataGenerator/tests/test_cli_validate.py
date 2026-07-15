import json

from dummygen.cli import main

SCHEMA = {
    "type": "object",
    "required": ["orderId"],
    "properties": {
        "orderId": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "quantity": {"type": "integer"},
                    "unitPrice": {"type": "integer"},
                },
            },
        },
        "payment": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "integer",
                    "x-generator": {"derivedFrom": "items", "formula": "sum(quantity*unitPrice)"},
                }
            },
        },
    },
}


def _write_schema(tmp_path):
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(SCHEMA), encoding="utf-8")
    return schema_file


def test_validate_command_passes_for_consistent_data(tmp_path):
    schema_file = _write_schema(tmp_path)
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps([
        {"orderId": "ORD-1", "items": [{"quantity": 2, "unitPrice": 10}], "payment": {"amount": 20}}
    ]), encoding="utf-8")

    exit_code = main(["validate", "--schema", str(schema_file), "--data", str(data_file)])

    assert exit_code == 0


def test_validate_command_fails_for_inconsistent_data(tmp_path, capsys):
    schema_file = _write_schema(tmp_path)
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps([
        {"orderId": "ORD-1", "items": [{"quantity": 2, "unitPrice": 10}], "payment": {"amount": 999}}
    ]), encoding="utf-8")

    exit_code = main(["validate", "--schema", str(schema_file), "--data", str(data_file)])

    assert exit_code != 0
    captured = capsys.readouterr()
    assert "payment.amount" in captured.err


def test_generate_with_validate_flag_writes_file_when_consistent(tmp_path):
    schema_file = _write_schema(tmp_path)
    output_file = tmp_path / "out.json"

    exit_code = main([
        "generate",
        "--schema", str(schema_file),
        "--count", "5",
        "--output", str(output_file),
        "--seed", "1",
        "--validate",
    ])

    assert exit_code == 0
    assert output_file.exists()
