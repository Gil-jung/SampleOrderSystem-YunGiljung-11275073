import random

from dummygen.generator import generate_field


def test_generate_field_dispatches_by_type():
    rng = random.Random(1)

    assert isinstance(generate_field({"type": "integer"}, rng), int)
    assert isinstance(generate_field({"type": "boolean"}, rng), bool)
    assert isinstance(generate_field({"type": "string"}, rng), str)
    assert generate_field({"type": "string", "enum": ["A", "B"]}, rng) in ["A", "B"]


def test_generate_field_object_recurses_into_properties():
    rng = random.Random(1)
    field_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "x-generator": {"choices": ["alice"]}},
            "age": {"type": "integer", "x-generator": {"min": 5, "max": 5}},
        },
    }

    value = generate_field(field_schema, rng)

    assert value == {"name": "alice", "age": 5}


def test_generate_field_array_respects_min_max_items():
    rng = random.Random(1)
    field_schema = {
        "type": "array",
        "items": {"type": "integer", "x-generator": {"min": 1, "max": 1}},
        "x-generator": {"minItems": 3, "maxItems": 3},
    }

    value = generate_field(field_schema, rng)

    assert value == [1, 1, 1]


def test_generate_field_unknown_type_raises():
    rng = random.Random(1)

    import pytest

    with pytest.raises(ValueError):
        generate_field({"type": "unsupported"}, rng)
