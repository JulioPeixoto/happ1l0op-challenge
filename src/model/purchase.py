from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class UserIntent(str, Enum):
    PURCHASE = "purchase"
    CHECK_STOCK = "check_stock"
    LIST_PRODUCTS = "list_products"
    UNKNOWN = "unknown"


class PurchaseIntent(BaseModel):
    intent: UserIntent = Field(description="User's intent")
    product_name: Optional[str] = Field(description="Name of the soda product")
    quantity: Optional[int] = Field(description="Quantity requested", ge=1)
    confidence: float = Field(description="Confidence level 0-1", ge=0, le=1)

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "intent": "purchase",
                    "product_name": "Coca-Cola",
                    "quantity": 3,
                    "confidence": 0.95,
                }
            ]
        }


class ChatRequest(BaseModel):
    message: str


class AIResponse(BaseModel):
    success: bool
    message: str
    purchase_intent: Optional[PurchaseIntent] = None
    transaction_id: Optional[int] = None
    total_price: Optional[float] = None
    products: Optional[List[dict]] = None
