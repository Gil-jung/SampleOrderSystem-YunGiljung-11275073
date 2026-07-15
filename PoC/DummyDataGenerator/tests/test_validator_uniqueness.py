from dummygen.validator import validate_uniqueness


def test_validate_uniqueness_passes_when_all_values_distinct():
    records = [{"orderId": "ORD-1"}, {"orderId": "ORD-2"}, {"orderId": "ORD-3"}]

    errors = validate_uniqueness(records, "orderId")

    assert errors == []


def test_validate_uniqueness_flags_duplicates():
    records = [{"orderId": "ORD-1"}, {"orderId": "ORD-2"}, {"orderId": "ORD-1"}]

    errors = validate_uniqueness(records, "orderId")

    assert len(errors) == 1
    assert "ORD-1" in errors[0]


def test_validate_uniqueness_supports_nested_field_path():
    records = [
        {"customer": {"customerId": "CUST-1"}},
        {"customer": {"customerId": "CUST-1"}},
    ]

    errors = validate_uniqueness(records, "customer.customerId")

    assert len(errors) == 1
    assert "CUST-1" in errors[0]
