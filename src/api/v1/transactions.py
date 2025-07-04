from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime

from model.transaction import TransactionResponse
from service.transaction_service import TransactionService
from db.database import get_session

router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=List[TransactionResponse])
def get_transaction_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    service = TransactionService(session)
    return service.get_all_transactions(skip, limit)


@router.get("/transactions/summary/daily", response_model=dict)
def get_daily_summary(
    date: Optional[datetime] = Query(
        None, description="Data para o resumo (YYYY-MM-DD). Padrão é hoje."
    ),
    session: Session = Depends(get_session),
):
    service = TransactionService(session)
    return service.get_daily_summary(date)


@router.get("/transactions/recent", response_model=List[TransactionResponse])
def get_recent_transactions(
    hours: int = Query(
        24, gt=0, description="Número de horas passadas para buscar transações."
    ),
    session: Session = Depends(get_session),
):
    service = TransactionService(session)
    return service.get_recent_transactions(hours) 