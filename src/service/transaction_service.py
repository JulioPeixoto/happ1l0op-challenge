from sqlmodel import Session
from typing import List, Optional
from datetime import datetime

from src.db.repository.transaction_repository import TransactionRepository
from src.model.transaction import TransactionResponse


class TransactionService:
    def __init__(self, session: Session):
        self.repo = TransactionRepository(session)

    def get_all_transactions(
        self, skip: int = 0, limit: int = 100
    ) -> List[TransactionResponse]:
        transactions = self.repo.get_all(skip, limit)
        return [TransactionResponse.model_validate(t) for t in transactions]

    def get_daily_summary(self, date: Optional[datetime] = None) -> dict:
        summary = self.repo.get_daily_sales_summary(date)
        summary.pop("transactions", None)
        return summary

    def get_recent_transactions(self, hours: int = 24) -> List[TransactionResponse]:
        transactions = self.repo.get_recent_transactions(hours)
        return [TransactionResponse.model_validate(t) for t in transactions] 