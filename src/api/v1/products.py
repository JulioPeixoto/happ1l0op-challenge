from fastapi import APIRouter, Depends
from sqlmodel import Session
from model.transaction import AIResponse
from service.purchase_service import PurchaseService
from db.database import get_session

router = APIRouter(tags=["products"])


@router.get("/products", response_model=AIResponse)
def list_available_products(session: Session = Depends(get_session)):
    """📋 Get all available products"""
    purchase_service = PurchaseService(session)
    return purchase_service.get_available_products()
