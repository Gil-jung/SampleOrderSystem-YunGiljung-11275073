import os

from dummygen.generator import generate_records
from dummygen.schema import load_schema

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "order-schema.json")


def test_order_schema_generates_expected_structure():
    schema = load_schema(SCHEMA_PATH)

    records = generate_records(schema, count=10, seed=123)

    assert len(records) == 10
    for order in records:
        assert order["orderId"].startswith("ORD-")
        assert order["status"] in ["PAID", "CANCELLED", "PENDING"]
        assert order["customer"]["customerId"].startswith("CUST-")
        assert 1 <= len(order["items"]) <= 3
        for item in order["items"]:
            assert item["quantity"] >= 1
            assert item["unitPrice"] >= 1000
        assert order["payment"]["method"] in ["CARD", "CASH", "TRANSFER"]
        assert order["shipment"]["trackingNo"].startswith("TRK-")


def test_order_schema_ids_are_unique_across_records():
    schema = load_schema(SCHEMA_PATH)

    records = generate_records(schema, count=20, seed=1)

    order_ids = [r["orderId"] for r in records]
    assert len(order_ids) == len(set(order_ids))


def test_order_schema_payment_amount_matches_items_sum():
    schema = load_schema(SCHEMA_PATH)

    records = generate_records(schema, count=10, seed=99)

    for order in records:
        expected = sum(item["quantity"] * item["unitPrice"] for item in order["items"])
        assert order["payment"]["amount"] == expected
