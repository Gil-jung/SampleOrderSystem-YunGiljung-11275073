from dummygen.generator import generate_records


def test_generate_records_returns_requested_count():
    schema = {"type": "object", "properties": {"id": {"type": "integer"}}}

    records = generate_records(schema, count=5, seed=1)

    assert len(records) == 5


def test_generate_records_is_reproducible_with_same_seed():
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "x-generator": {"pattern": "ID-{seq:03d}"}},
            "value": {"type": "integer", "x-generator": {"min": 1, "max": 1000}},
        },
    }

    first = generate_records(schema, count=10, seed=42)
    second = generate_records(schema, count=10, seed=42)

    assert first == second


def test_generate_records_seq_increments_per_record():
    schema = {"type": "object", "properties": {"id": {"type": "string", "x-generator": {"pattern": "ID-{seq:03d}"}}}}

    records = generate_records(schema, count=3, seed=1)

    assert [r["id"] for r in records] == ["ID-000", "ID-001", "ID-002"]
