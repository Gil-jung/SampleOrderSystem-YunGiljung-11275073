import random

from dummygen.generator import generate_number


def test_generate_integer_within_range():
    rng = random.Random(42)
    field_schema = {"type": "integer", "x-generator": {"min": 1, "max": 10}}

    for _ in range(50):
        value = generate_number(field_schema, rng)
        assert isinstance(value, int)
        assert 1 <= value <= 10


def test_generate_number_float_within_range():
    rng = random.Random(42)
    field_schema = {"type": "number", "x-generator": {"min": 0.0, "max": 1.0}}

    for _ in range(50):
        value = generate_number(field_schema, rng)
        assert isinstance(value, float)
        assert 0.0 <= value <= 1.0


def test_generate_integer_defaults_when_no_range_given():
    rng = random.Random(42)
    field_schema = {"type": "integer"}

    value = generate_number(field_schema, rng)

    assert isinstance(value, int)
    assert 0 <= value <= 1000
