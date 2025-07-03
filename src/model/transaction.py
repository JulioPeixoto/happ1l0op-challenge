from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from enum import Enum

if TYPE_CHECKING:
    from src.model.product import Product

class TransactionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class TransactionBase(SQLModel):
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(gt=0, description="Quantity purchased")
    unit_price: Decimal = Field(decimal_places=2, description="Unit price at sale time")
    total_price: Decimal = Field(decimal_places=2, description="Total price")
    user_message: str = Field(description="Original user message")

class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    status: TransactionStatus = Field(default=TransactionStatus.SUCCESS)
    created_at: datetime = Field(default_factory=datetime.now)
    
    product: Optional["Product"] = Relationship(back_populates="transactions")

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    status: TransactionStatus
    created_at: datetime