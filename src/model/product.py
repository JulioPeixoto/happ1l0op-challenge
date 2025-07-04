from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime

if TYPE_CHECKING:
    from src.model.transaction import Transaction


class ProductBase(SQLModel):
    name: str = Field(max_length=100, description="Product name")
    description: Optional[str] = Field(default=None, max_length=255)
    price: Decimal = Field(decimal_places=2, description="Unit price")
    stock_quantity: int = Field(ge=0, description="Stock quantity")


class Product(ProductBase, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, max_length=50, description="Product SKU")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    transactions: List["Transaction"] = Relationship(back_populates="product")


class ProductCreate(ProductBase):
    sku: str


class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    sku: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
 