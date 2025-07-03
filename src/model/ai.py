from pydantic import BaseModel
from typing import Optional
from model.purchase import PurchaseIntent


class ChatRequest(BaseModel):
    message: str


class AIResponse(BaseModel):
    success: bool
    message: str
    purchase_intent: Optional[PurchaseIntent] = None
    transaction_id: Optional[int] = None
    total_price: Optional[float] = None
