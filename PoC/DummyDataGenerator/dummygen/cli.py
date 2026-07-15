import argparse
import json
import sys

from dummygen.generator import generate_records
from dummygen.schema import SchemaError, load_schema
from dummygen.validator import validate_consistency, validate_schema
from dummygen.writer import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dummy-gen")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate dummy data from a schema")
    generate.add_argument("--schema", required=True, help="Path to the schema JSON file")
    generate.add_argument("--count", type=int, default=1, help="Number of records to generate")
    generate.add_argument("--output", required=True, help="Path to write the generated JSON file")
    generate.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")
    generate.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated records against the schema before writing output",
    )

    validate = subparsers.add_parser("validate", help="Validate a JSON data file against a schema")
    validate.add_argument("--schema", required=True, help="Path to the schema JSON file")
    validate.add_argument("--data", required=True, help="Path to the JSON data file to validate")

    return parser


def _validate_records(records: list, schema: dict) -> list:
    errors = []
    for index, record in enumerate(records):
        for error in validate_schema(record, schema):
            errors.append(f"record[{index}] {error}")
        for error in validate_consistency(record, schema):
            errors.append(f"record[{index}] {error}")
    return errors


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        try:
            schema = load_schema(args.schema)
        except SchemaError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        records = generate_records(schema, count=args.count, seed=args.seed)

        if args.validate:
            errors = _validate_records(records, schema)
            if errors:
                for error in errors:
                    print(f"Error: {error}", file=sys.stderr)
                return 1

        write_json(records, args.output)
        return 0

    if args.command == "validate":
        try:
            schema = load_schema(args.schema)
            with open(args.data, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (SchemaError, OSError, json.JSONDecodeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        errors = _validate_records(records, schema)
        if errors:
            for error in errors:
                print(f"Error: {error}", file=sys.stderr)
            return 1
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
