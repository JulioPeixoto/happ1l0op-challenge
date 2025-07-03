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


class UserIntent(str, Enum):
    PURCHASE = "purchase"
    CHECK_STOCK = "check_stock"
    LIST_PRODUCTS = "list_products"
    UNKNOWN = "unknown"


class TransactionBase(SQLModel):
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(gt=0, description="Quantity purchased")
    unit_price: Decimal = Field(decimal_places=2, description="Unit price at sale time")
    total_price: Decimal = Field(decimal_places=2, description="Total price")
    user_message: str = Field(description="Original user message")


class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    intent: UserIntent = Field(default=UserIntent.PURCHASE)
    confidence: Optional[float] = Field(default=None, description="AI confidence level")
    created_at: datetime = Field(default_factory=datetime.now)

    product: Optional["Product"] = Relationship(back_populates="transactions")


class TransactionCreate(TransactionBase):
    intent: Optional[UserIntent] = UserIntent.PURCHASE
    confidence: Optional[float] = None


class TransactionResponse(TransactionBase):
    id: int
    status: TransactionStatus
    intent: UserIntent
    confidence: Optional[float]
    created_at: datetime


class PurchaseIntent(SQLModel):
    intent: UserIntent
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    confidence: float = Field(default=0.0, ge=0, le=1)


class AIResponse(SQLModel):
    success: bool
    message: str
    transaction_id: Optional[int] = None
    total_price: Optional[float] = None
    products: Optional[list] = None
