from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from model.product import Product, ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Optional[Product]:
        statement = select(Product).where(Product.sku == sku)
        return self.session.exec(statement).first()

    def get_available_products(self) -> List[Product]:
        statement = select(Product).where(Product.stock_quantity > 0)
        return self.session.exec(statement).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        statement = select(Product).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def update_stock(self, product_id: int, quantity_sold: int) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product and product.stock_quantity >= quantity_sold:
            product.stock_quantity -= quantity_sold
            product.updated_at = datetime.now()
            self.session.commit()
            self.session.refresh(product)
            return product
        return None

    def search_by_name(self, name: str) -> List[Product]:
        statement = select(Product).where(
            Product.name.ilike(f"%{name}%"),
        )
        return self.session.exec(statement).all()

    def check_stock_availability(self, product_id: int, quantity: int) -> bool:
        product = self.get_by_id(product_id)
        return product is not None and product.stock_quantity >= quantity

    def update(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product:
            for field, value in product_data.model_dump(exclude_unset=True).items():
                setattr(product, field, value)
            product.updated_at = datetime.now()
            self.session.commit()
            self.session.refresh(product)
        return product

    def delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        if product:
            product.is_active = False
            product.updated_at = datetime.now()
            self.session.commit()
            return True
        return False

    def restock(self, product_id: int, quantity: int) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product:
            product.stock_quantity += quantity
            product.updated_at = datetime.now()
            self.session.commit()
            self.session.refresh(product)
        return product

    def get_low_stock_products(self, threshold: int = 5) -> List[Product]:
        statement = select(Product).where(
            Product.stock_quantity <= threshold, Product.stock_quantity > 0
        )
        return self.session.exec(statement).all()

    def get_out_of_stock_products(self) -> List[Product]:
        statement = select(Product).where(Product.stock_quantity == 0)
        return self.session.exec(statement).all()
