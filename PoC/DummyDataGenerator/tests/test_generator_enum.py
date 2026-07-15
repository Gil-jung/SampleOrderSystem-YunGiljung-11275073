import random

import pytest

from dummygen.generator import generate_enum


def test_generate_enum_picks_from_list():
    rng = random.Random(1)
    field_schema = {"type": "string", "enum": ["PAID", "CANCELLED", "PENDING"]}

    for _ in range(30):
        value = generate_enum(field_schema, rng)
        assert value in ["PAID", "CANCELLED", "PENDING"]


def test_generate_enum_respects_weights():
    rng = random.Random(1)
    field_schema = {
        "type": "string",
        "enum": ["PAID", "CANCELLED"],
        "x-generator": {"weights": [1, 0]},
    }

    for _ in range(30):
        assert generate_enum(field_schema, rng) == "PAID"


def test_generate_enum_requires_non_empty_enum():
    rng = random.Random(1)
    field_schema = {"type": "string", "enum": []}

    with pytest.raises(ValueError):
        generate_enum(field_schema, rng)
