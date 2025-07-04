from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta

from model.transaction import (
    Transaction,
    TransactionCreate,
    TransactionStatus,
    UserIntent,
)


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, transaction_data: TransactionCreate) -> Transaction:
        transaction = Transaction(**transaction_data.model_dump())
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        statement = (
            select(Transaction)
            .offset(skip)
            .limit(limit)
            .order_by(Transaction.created_at.desc())
        )
        return self.session.exec(statement).all()

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.session.get(Transaction, transaction_id)

    def get_recent_transactions(self, hours: int = 24) -> List[Transaction]:
        since = datetime.now() - timedelta(hours=hours)
        statement = (
            select(Transaction)
            .where(Transaction.created_at >= since)
            .order_by(Transaction.created_at.desc())
        )
        return self.session.exec(statement).all()

    def get_successful_transactions(
        self, start_date: Optional[datetime] = None
    ) -> List[Transaction]:
        statement = select(Transaction).where(
            Transaction.status == TransactionStatus.SUCCESS
        )
        if start_date:
            statement = statement.where(Transaction.created_at >= start_date)
        return (
            self.session.exec(statement).order_by(Transaction.created_at.desc()).all()
        )

    def get_sales_by_product(self, product_id: int) -> List[Transaction]:
        statement = select(Transaction).where(
            Transaction.product_id == product_id,
            Transaction.status == TransactionStatus.SUCCESS,
        )
        return self.session.exec(statement).all()

    def get_total_sales(self, start_date: Optional[datetime] = None) -> float:
        statement = select(Transaction).where(
            Transaction.status == TransactionStatus.SUCCESS
        )
        if start_date:
            statement = statement.where(Transaction.created_at >= start_date)

        transactions = self.session.exec(statement).all()
        return sum(float(t.total_price) for t in transactions)

    def get_daily_sales_summary(self, date: Optional[datetime] = None) -> dict:
        if date is None:
            date = datetime.now()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        statement = select(Transaction).where(
            Transaction.created_at >= start_of_day,
            Transaction.created_at < end_of_day,
            Transaction.status == TransactionStatus.SUCCESS,
        )

        transactions = self.session.exec(statement).all()

        return {
            "date": date.strftime("%Y-%m-%d"),
            "total_transactions": len(transactions),
            "total_revenue": sum(float(t.total_price) for t in transactions),
            "total_items_sold": sum(t.quantity for t in transactions),
            "transactions": transactions,
        }

    def get_failed_transactions(self, hours: int = 24) -> List[Transaction]:
        since = datetime.now() - timedelta(hours=hours)
        statement = (
            select(Transaction)
            .where(
                Transaction.status == TransactionStatus.FAILED,
                Transaction.created_at >= since,
            )
            .order_by(Transaction.created_at.desc())
        )
        return self.session.exec(statement).all()

    def get_transactions_by_intent(self, intent: UserIntent) -> List[Transaction]:
        statement = select(Transaction).where(Transaction.intent == intent)
        return self.session.exec(statement).all()

    def update_status(
        self, transaction_id: int, status: TransactionStatus
    ) -> Optional[Transaction]:
        transaction = self.get_by_id(transaction_id)
        if transaction:
            transaction.status = status
            self.session.commit()
            self.session.refresh(transaction)
        return transaction

    def get_popular_products(self, days: int = 7) -> List[dict]:
        since = datetime.now() - timedelta(days=days)
        statement = select(Transaction).where(
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= since,
        )

        transactions = self.session.exec(statement).all()

        product_sales = {}
        for transaction in transactions:
            product_id = transaction.product_id
            if product_id not in product_sales:
                product_sales[product_id] = {
                    "product_id": product_id,
                    "total_quantity": 0,
                    "total_revenue": 0.0,
                    "transaction_count": 0,
                }
            product_sales[product_id]["total_quantity"] += transaction.quantity
            product_sales[product_id]["total_revenue"] += float(transaction.total_price)
            product_sales[product_id]["transaction_count"] += 1

        return sorted(
            product_sales.values(), key=lambda x: x["total_quantity"], reverse=True
        )

    def get_hourly_sales_pattern(self, days: int = 7) -> List[dict]:
        since = datetime.now() - timedelta(days=days)
        statement = select(Transaction).where(
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= since,
        )

        transactions = self.session.exec(statement).all()

        hourly_sales = {}
        for transaction in transactions:
            hour = transaction.created_at.hour
            if hour not in hourly_sales:
                hourly_sales[hour] = {
                    "hour": hour,
                    "transaction_count": 0,
                    "total_revenue": 0.0,
                    "total_items": 0,
                }
            hourly_sales[hour]["transaction_count"] += 1
            hourly_sales[hour]["total_revenue"] += float(transaction.total_price)
            hourly_sales[hour]["total_items"] += transaction.quantity

        return sorted(hourly_sales.values(), key=lambda x: x["hour"])
