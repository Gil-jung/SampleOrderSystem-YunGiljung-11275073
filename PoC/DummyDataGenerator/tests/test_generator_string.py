import random
import string

from dummygen.generator import generate_string


def test_generate_string_using_seq_pattern():
    rng = random.Random(1)
    field_schema = {"type": "string", "x-generator": {"pattern": "ORD-{seq:04d}"}}

    value = generate_string(field_schema, rng, seq=7)

    assert value == "ORD-0007"


def test_generate_string_using_choices():
    rng = random.Random(1)
    field_schema = {"type": "string", "x-generator": {"choices": ["apple", "banana"]}}

    for _ in range(20):
        value = generate_string(field_schema, rng, seq=0)
        assert value in ("apple", "banana")


def test_generate_string_default_random_alnum():
    rng = random.Random(1)
    field_schema = {"type": "string"}

    value = generate_string(field_schema, rng, seq=0)

    assert isinstance(value, str)
    assert len(value) == 8
    assert all(ch in string.ascii_letters + string.digits for ch in value)
