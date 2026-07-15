import random
import re
import string
from datetime import datetime, timedelta

DEFAULT_MIN = 0
DEFAULT_MAX = 1000
DEFAULT_STRING_LENGTH = 8
DEFAULT_DATE_START = "2020-01-01T00:00:00"
DEFAULT_DATE_END = "2029-12-31T23:59:59"


def generate_number(field_schema: dict, rng):
    options = field_schema.get("x-generator", {})
    minimum = options.get("min", DEFAULT_MIN)
    maximum = options.get("max", DEFAULT_MAX)

    if field_schema.get("type") == "integer":
        return rng.randint(int(minimum), int(maximum))
    return rng.uniform(float(minimum), float(maximum))


def generate_string(field_schema: dict, rng, seq: int = 0) -> str:
    options = field_schema.get("x-generator", {})

    if "pattern" in options:
        return options["pattern"].format(seq=seq)

    if "choices" in options:
        return rng.choice(options["choices"])

    alphabet = string.ascii_letters + string.digits
    return "".join(rng.choice(alphabet) for _ in range(DEFAULT_STRING_LENGTH))


def generate_boolean(field_schema: dict, rng) -> bool:
    options = field_schema.get("x-generator", {})
    true_ratio = options.get("true_ratio", 0.5)
    return rng.random() < true_ratio


def generate_enum(field_schema: dict, rng):
    values = field_schema.get("enum", [])
    if not values:
        raise ValueError("enum field schema must define a non-empty 'enum' list")

    options = field_schema.get("x-generator", {})
    weights = options.get("weights")
    if weights is not None:
        return rng.choices(values, weights=weights, k=1)[0]
    return rng.choice(values)


def generate_date(field_schema: dict, rng) -> str:
    options = field_schema.get("x-generator", {})
    start = datetime.fromisoformat(options.get("start", DEFAULT_DATE_START))
    end = datetime.fromisoformat(options.get("end", DEFAULT_DATE_END))

    delta_seconds = (end - start).total_seconds()
    offset = rng.uniform(0, delta_seconds)
    result = start + timedelta(seconds=offset)
    return result.isoformat()


DEFAULT_MIN_ITEMS = 1
DEFAULT_MAX_ITEMS = 3


def generate_object(field_schema: dict, rng, seq: int = 0) -> dict:
    properties = field_schema.get("properties", {})
    return {
        name: generate_field(sub_schema, rng, seq=seq)
        for name, sub_schema in properties.items()
    }


def generate_array(field_schema: dict, rng, seq: int = 0) -> list:
    item_schema = field_schema.get("items", {})
    options = field_schema.get("x-generator", {})
    min_items = options.get("minItems", DEFAULT_MIN_ITEMS)
    max_items = options.get("maxItems", DEFAULT_MAX_ITEMS)
    count = rng.randint(min_items, max_items)
    return [generate_field(item_schema, rng, seq=seq) for _ in range(count)]


_CUSTOM_GENERATORS = {}


def register_generator(name: str, func) -> None:
    _CUSTOM_GENERATORS[name] = func


def generate_field(field_schema: dict, rng, seq: int = 0):
    options = field_schema.get("x-generator", {})
    if "custom" in options:
        name = options["custom"]
        if name not in _CUSTOM_GENERATORS:
            raise ValueError(f"Unknown custom generator: {name!r}")
        return _CUSTOM_GENERATORS[name](field_schema, rng, seq)

    field_type = field_schema.get("type")

    if "enum" in field_schema:
        return generate_enum(field_schema, rng)
    if field_type == "object":
        return generate_object(field_schema, rng, seq=seq)
    if field_type == "array":
        return generate_array(field_schema, rng, seq=seq)
    if field_type in ("integer", "number"):
        return generate_number(field_schema, rng)
    if field_type == "string":
        if field_schema.get("format") == "date-time":
            return generate_date(field_schema, rng)
        return generate_string(field_schema, rng, seq=seq)
    if field_type == "boolean":
        return generate_boolean(field_schema, rng)

    raise ValueError(f"Unsupported field type: {field_type!r}")


_SUM_FORMULA_RE = re.compile(r"^sum\((.+)\)$")


def _parse_sum_formula(formula: str) -> list:
    match = _SUM_FORMULA_RE.match(formula.strip())
    if not match:
        raise ValueError(f"Unsupported derived field formula: {formula!r}")
    return [term.strip() for term in match.group(1).split("*")]


def _evaluate_sum_formula(items: list, formula: str):
    field_names = _parse_sum_formula(formula)
    total = 0
    for item in items:
        product = 1
        for field_name in field_names:
            product *= item[field_name]
        total += product
    return total


def apply_derived_fields(node, schema: dict, root=None):
    if root is None:
        root = node

    field_type = schema.get("type")
    if field_type == "object":
        for name, sub_schema in schema.get("properties", {}).items():
            options = sub_schema.get("x-generator", {})
            if "derivedFrom" in options:
                source = root.get(options["derivedFrom"], [])
                node[name] = _evaluate_sum_formula(source, options["formula"])
            else:
                apply_derived_fields(node[name], sub_schema, root)
    elif field_type == "array":
        item_schema = schema.get("items", {})
        for item in node:
            apply_derived_fields(item, item_schema, root)


def generate_record(schema: dict, rng, seq: int = 0):
    record = generate_field(schema, rng, seq=seq)
    apply_derived_fields(record, schema)
    return record


def generate_records(schema: dict, count: int, seed=None) -> list:
    rng = random.Random(seed)
    return [generate_record(schema, rng, seq=i) for i in range(count)]
