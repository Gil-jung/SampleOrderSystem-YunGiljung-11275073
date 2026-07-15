from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    price: int

    def __post_init__(self):
        if self.price < 0:
            raise ValueError(f"상품 가격은 음수일 수 없습니다: {self.price}")
