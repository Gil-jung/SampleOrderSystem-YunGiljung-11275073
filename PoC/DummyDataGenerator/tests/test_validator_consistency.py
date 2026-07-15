from dummygen.validator import validate_consistency

SCHEMA = {
    "type": "object",
    "properties": {
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


def test_validate_consistency_passes_for_correct_derived_value():
    record = {
        "items": [{"quantity": 2, "unitPrice": 10}, {"quantity": 1, "unitPrice": 5}],
        "payment": {"amount": 25},
    }

    errors = validate_consistency(record, SCHEMA)

    assert errors == []


def test_validate_consistency_flags_mismatched_derived_value():
    record = {
        "items": [{"quantity": 2, "unitPrice": 10}],
        "payment": {"amount": 999},
    }

    errors = validate_consistency(record, SCHEMA)

    assert len(errors) == 1
    assert "payment.amount" in errors[0]
