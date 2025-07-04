from fastapi import APIRouter
from .v1.products import router as products_router
from .v1.vending import router as vending_router
from .v1.transactions import router as transactions_router

api_router = APIRouter()

api_router.include_router(products_router, prefix="/v1")
api_router.include_router(vending_router, prefix="/v1")
api_router.include_router(transactions_router, prefix="/v1")