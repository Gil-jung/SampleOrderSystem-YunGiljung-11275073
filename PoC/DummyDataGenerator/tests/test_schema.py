import json

from dummygen.schema import load_schema, SchemaError
import pytest


def test_load_schema_reads_json_file(tmp_path):
    schema_dict = {"type": "object", "properties": {"name": {"type": "string"}}}
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema_dict), encoding="utf-8")

    loaded = load_schema(str(schema_file))

    assert loaded == schema_dict


def test_load_schema_raises_for_missing_file(tmp_path):
    missing = tmp_path / "does-not-exist.json"

    with pytest.raises(SchemaError):
        load_schema(str(missing))


def test_load_schema_raises_for_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(SchemaError):
        load_schema(str(bad_file))
