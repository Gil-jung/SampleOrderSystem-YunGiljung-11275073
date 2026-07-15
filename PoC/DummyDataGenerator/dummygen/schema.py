import json


class SchemaError(Exception):
    """Raised when a schema file cannot be loaded or parsed."""


def load_schema(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        raise SchemaError(f"Could not read schema file: {path}") from exc

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Invalid JSON in schema file: {path}") from exc
