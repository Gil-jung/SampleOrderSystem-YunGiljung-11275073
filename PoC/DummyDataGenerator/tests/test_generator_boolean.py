import random

from dummygen.generator import generate_boolean


def test_generate_boolean_default_returns_bool():
    rng = random.Random(1)
    field_schema = {"type": "boolean"}

    value = generate_boolean(field_schema, rng)

    assert isinstance(value, bool)


def test_generate_boolean_true_ratio_zero_always_false():
    rng = random.Random(1)
    field_schema = {"type": "boolean", "x-generator": {"true_ratio": 0.0}}

    for _ in range(20):
        assert generate_boolean(field_schema, rng) is False


def test_generate_boolean_true_ratio_one_always_true():
    rng = random.Random(1)
    field_schema = {"type": "boolean", "x-generator": {"true_ratio": 1.0}}

    for _ in range(20):
        assert generate_boolean(field_schema, rng) is True
