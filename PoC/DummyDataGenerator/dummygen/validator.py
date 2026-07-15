from dummygen.generator import _evaluate_sum_formula

_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
}


def validate_consistency(record: dict, schema: dict) -> list:
    errors = []
    _check(record, schema, record, "", errors)
    return errors


def _check(node, schema, root, path, errors):
    field_type = schema.get("type")

    if field_type == "object":
        for name, sub_schema in schema.get("properties", {}).items():
            sub_path = f"{path}.{name}" if path else name
            options = sub_schema.get("x-generator", {})
            if "derivedFrom" in options:
                source = root.get(options["derivedFrom"], [])
                expected = _evaluate_sum_formula(source, options["formula"])
                actual = node.get(name)
                if actual != expected:
                    errors.append(f"{sub_path}: expected {expected}, got {actual}")
            else:
                _check(node[name], sub_schema, root, sub_path, errors)
    elif field_type == "array":
        item_schema = schema.get("items", {})
        for index, item in enumerate(node):
            _check(item, item_schema, root, f"{path}[{index}]", errors)


def _get_path(record: dict, field_path: str):
    node = record
    for part in field_path.split("."):
        node = node[part]
    return node


def validate_schema(value, schema: dict, path: str = "") -> list:
    errors = []
    field_type = schema.get("type")
    label = path or "<root>"

    if field_type in _TYPE_MAP and not isinstance(value, _TYPE_MAP[field_type]):
        errors.append(f"{label}: expected type {field_type}, got {type(value).__name__}")
        return errors

    if field_type == "object":
        for name in schema.get("required", []):
            sub_path = f"{path}.{name}" if path else name
            if name not in value:
                errors.append(f"{sub_path}: required field missing")
        for name, sub_schema in schema.get("properties", {}).items():
            if name in value:
                sub_path = f"{path}.{name}" if path else name
                errors.extend(validate_schema(value[name], sub_schema, sub_path))
    elif field_type == "array":
        item_schema = schema.get("items", {})
        for index, item in enumerate(value):
            errors.extend(validate_schema(item, item_schema, f"{label}[{index}]"))

    return errors


def validate_uniqueness(records: list, field_path: str) -> list:
    seen = {}
    errors = []
    for index, record in enumerate(records):
        value = _get_path(record, field_path)
        if value in seen:
            errors.append(
                f"Duplicate value {value!r} at {field_path} (records {seen[value]} and {index})"
            )
        else:
            seen[value] = index
    return errors
