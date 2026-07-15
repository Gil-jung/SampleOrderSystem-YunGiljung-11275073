import random

import pytest

from dummygen.generator import generate_field, register_generator


def test_register_generator_is_used_for_custom_field():
    register_generator("always_hello", lambda field_schema, rng, seq: "hello")
    rng = random.Random(1)
    field_schema = {"type": "string", "x-generator": {"custom": "always_hello"}}

    value = generate_field(field_schema, rng)

    assert value == "hello"


def test_register_generator_receives_seq():
    register_generator("echo_seq", lambda field_schema, rng, seq: f"seq-{seq}")
    rng = random.Random(1)
    field_schema = {"type": "string", "x-generator": {"custom": "echo_seq"}}

    value = generate_field(field_schema, rng, seq=9)

    assert value == "seq-9"


def test_unknown_custom_generator_raises():
    rng = random.Random(1)
    field_schema = {"type": "string", "x-generator": {"custom": "does_not_exist"}}

    with pytest.raises(ValueError):
        generate_field(field_schema, rng)
