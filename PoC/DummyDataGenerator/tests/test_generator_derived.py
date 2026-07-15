import random

from dummygen.generator import generate_record


def test_derived_field_sums_sibling_array_product():
    rng = random.Random(1)
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "x-generator": {"minItems": 2, "maxItems": 2},
                "items": {
                    "type": "object",
                    "properties": {
                        "quantity": {"type": "integer", "x-generator": {"min": 2, "max": 2}},
                        "unitPrice": {"type": "integer", "x-generator": {"min": 10, "max": 10}},
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

    record = generate_record(schema, rng, seq=0)

    assert len(record["items"]) == 2
    expected = sum(item["quantity"] * item["unitPrice"] for item in record["items"])
    assert record["payment"]["amount"] == expected
    assert expected == 40
