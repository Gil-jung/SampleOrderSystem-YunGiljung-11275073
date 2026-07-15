import random
from datetime import datetime

from dummygen.generator import generate_date


def test_generate_date_within_range():
    rng = random.Random(1)
    field_schema = {
        "type": "string",
        "format": "date-time",
        "x-generator": {"start": "2026-01-01T00:00:00", "end": "2026-01-31T23:59:59"},
    }

    for _ in range(30):
        value = generate_date(field_schema, rng)
        parsed = datetime.fromisoformat(value)
        assert datetime(2026, 1, 1) <= parsed <= datetime(2026, 1, 31, 23, 59, 59)


def test_generate_date_uses_default_range_when_unspecified():
    rng = random.Random(1)
    field_schema = {"type": "string", "format": "date-time"}

    value = generate_date(field_schema, rng)

    # should not raise, and should be a valid ISO 8601 datetime string
    datetime.fromisoformat(value)
