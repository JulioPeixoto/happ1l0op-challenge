from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from model.product import ProductCreate, ProductUpdate, ProductResponse
from service.product_service import ProductService
from db.database import get_session

router = APIRouter(tags=["products"])

@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    service = ProductService(session)
    return service.create_product(product)

@router.get("/products", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    available_only: bool = Query(False),
    session: Session = Depends(get_session)
):
    service = ProductService(session)
    if available_only:
        return service.get_available_products()
    return service.get_all_products(skip, limit)

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, session: Session = Depends(get_session)):
    service = ProductService(session)
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, 
    product_data: ProductUpdate, 
    session: Session = Depends(get_session)
):
    service = ProductService(session)
    product = service.update_product(product_id, product_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    service = ProductService(session)
    deleted = service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")

@router.post("/products/{product_id}/restock", response_model=ProductResponse)
def restock_product(
    product_id: int, 
    quantity: int = Query(..., gt=0),
    session: Session = Depends(get_session)
):
    service = ProductService(session)
    product = service.restock_product(product_id, quantity)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/products/search/{name}", response_model=List[ProductResponse])
def search_products(name: str, session: Session = Depends(get_session)):
    service = ProductService(session)
    return service.search_products(name)
