from dummygen.validator import validate_schema

SCHEMA = {
    "type": "object",
    "required": ["orderId", "customer"],
    "properties": {
        "orderId": {"type": "string"},
        "customer": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"quantity": {"type": "integer"}},
            },
        },
    },
}


def test_validate_schema_passes_for_valid_record():
    record = {
        "orderId": "ORD-1",
        "customer": {"name": "Alice"},
        "items": [{"quantity": 2}],
    }

    assert validate_schema(record, SCHEMA) == []


def test_validate_schema_flags_missing_required_field():
    record = {"customer": {"name": "Alice"}}

    errors = validate_schema(record, SCHEMA)

    assert any("orderId" in e for e in errors)


def test_validate_schema_flags_type_mismatch():
    record = {"orderId": 123, "customer": {"name": "Alice"}}

    errors = validate_schema(record, SCHEMA)

    assert any("orderId" in e and "type" in e for e in errors)


def test_validate_schema_flags_nested_missing_required_field():
    record = {"orderId": "ORD-1", "customer": {}}

    errors = validate_schema(record, SCHEMA)

    assert any("customer.name" in e for e in errors)


def test_validate_schema_flags_array_item_type_mismatch():
    record = {
        "orderId": "ORD-1",
        "customer": {"name": "Alice"},
        "items": [{"quantity": "not-a-number"}],
    }

    errors = validate_schema(record, SCHEMA)

    assert any("items[0].quantity" in e for e in errors)
