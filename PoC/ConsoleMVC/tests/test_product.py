import pytest

from model.product import Product


def test_상품_생성_시_속성이_저장된다():
    product = Product("P001", "아메리카노", 4500)

    assert product.product_id == "P001"
    assert product.name == "아메리카노"
    assert product.price == 4500


def test_음수_가격은_거부된다():
    with pytest.raises(ValueError):
        Product("P001", "아메리카노", -1000)


def test_상품은_불변이다():
    product = Product("P001", "아메리카노", 4500)
    with pytest.raises(Exception):
        product.price = 5000
