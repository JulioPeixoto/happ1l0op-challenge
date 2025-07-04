from sqlmodel import Session
from typing import List, Optional

from src.db.repository.product_repository import ProductRepository
from src.model.product import Product, ProductCreate, ProductUpdate, ProductResponse


class ProductService:
    def __init__(self, session: Session):
        self.repo = ProductRepository(session)

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        product = self.repo.create(product_data)
        return ProductResponse.model_validate(product)

    def get_product(self, product_id: int) -> Optional[ProductResponse]:
        product = self.repo.get_by_id(product_id)
        return ProductResponse.model_validate(product) if product else None

    def get_all_products(
        self, skip: int = 0, limit: int = 100
    ) -> List[ProductResponse]:
        products = self.repo.get_all(skip, limit)
        return [ProductResponse.model_validate(p) for p in products]

    def get_available_products(self) -> List[ProductResponse]:
        products = self.repo.get_available_products()
        return [ProductResponse.model_validate(p) for p in products]

    def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[ProductResponse]:
        product = self.repo.update(product_id, product_data)
        return ProductResponse.model_validate(product) if product else None

    def delete_product(self, product_id: int) -> bool:
        return self.repo.delete(product_id)

    def restock_product(
        self, product_id: int, quantity: int
    ) -> Optional[ProductResponse]:
        product = self.repo.restock(product_id, quantity)
        return ProductResponse.model_validate(product) if product else None

    def search_products(self, name: str) -> List[ProductResponse]:
        products = self.repo.search_by_name(name)
        return [ProductResponse.model_validate(p) for p in products]
