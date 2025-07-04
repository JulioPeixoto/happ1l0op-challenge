from sqlmodel import Session
from typing import Optional

from db.repository.product_repository import ProductRepository
from db.repository.transaction_repository import TransactionRepository
from model.transaction import (
    TransactionCreate,
    TransactionStatus,
    AIResponse,
)
from model.purchase import PurchaseIntent, UserIntent
from model.product import Product


class PurchaseService:
    def __init__(self, session: Session):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.transaction_repo = TransactionRepository(session)

    def process_purchase(self, intent: PurchaseIntent, user_message: str) -> AIResponse:
        if intent.intent != UserIntent.PURCHASE:
            return self._handle_non_purchase_intent(intent)

        if not intent.product_name or not intent.quantity:
            return AIResponse(
                success=False,
                message="Please specify which product and how many you want. For example: 'I want 2 cokes'",
            )

        product = self._find_product_by_name(intent.product_name)
        if not product:
            available_products = self._get_available_products_list()
            return AIResponse(
                success=False,
                message=f"Sorry, I don't have '{intent.product_name}'. Available products: {available_products}",
            )

        if product.stock_quantity < intent.quantity:
            return AIResponse(
                success=False,
                message=f"Sorry, I only have {product.stock_quantity} {product.name} in stock.",
            )

        unit_price = product.price
        total_price = unit_price * intent.quantity

        transaction_data = TransactionCreate(
            product_id=product.id,
            quantity=intent.quantity,
            unit_price=unit_price,
            total_price=total_price,
            user_message=user_message,
            intent=intent.intent,
            confidence=intent.confidence,
        )

        try:
            transaction = self.transaction_repo.create(transaction_data)
            updated_product = self.product_repo.update_stock(
                product.id, intent.quantity
            )

            if not updated_product:
                transaction.status = TransactionStatus.FAILED
                self.session.commit()
                return AIResponse(
                    success=False, message="Transaction failed. Please try again."
                )

            transaction.status = TransactionStatus.SUCCESS
            self.session.commit()

            return AIResponse(
                success=True,
                message=f"🥤 Great! I've dispensed {intent.quantity} {product.name} for ${total_price:.2f}. Enjoy your drink!",
                transaction_id=transaction.id,
                total_price=float(total_price),
            )

        except Exception as e:
            return AIResponse(
                success=False,
                message="Sorry, something went wrong with your purchase. Please try again.",
            )

    def _handle_non_purchase_intent(self, intent: PurchaseIntent) -> AIResponse:
        if intent.intent == UserIntent.LIST_PRODUCTS:
            return self.get_available_products()

        elif intent.intent == UserIntent.CHECK_STOCK:
            if intent.product_name:
                return self._check_product_stock(intent.product_name)
            else:
                return AIResponse(
                    success=True,
                    message="Which product would you like to check stock for?",
                )

        else:
            return AIResponse(
                success=True,
                message="I'm a soda vending machine! You can:\n• Buy products: 'I want 2 cokes'\n• Check inventory: 'What do you have?'\n• Check stock: 'How many sprites are left?'",
            )

    def get_available_products(self) -> AIResponse:
        products = self.product_repo.get_available_products()

        if not products:
            return AIResponse(
                success=True,
                message="Sorry, we're currently out of stock on all products.",
            )

        product_list = []
        for product in products:
            product_list.append(
                f"• {product.name}: ${product.price:.2f} ({product.stock_quantity} available)"
            )

        message = "Available Products:\n" + "\n".join(product_list)

        return AIResponse(
            success=True,
            message=message,
            products=[
                {
                    "id": p.id,
                    "name": p.name,
                    "price": float(p.price),
                    "stock": p.stock_quantity,
                }
                for p in products
            ],
        )

    def _check_product_stock(self, product_name: str) -> AIResponse:
        product = self._find_product_by_name(product_name)

        if not product:
            available_products = self._get_available_products_list()
            return AIResponse(
                success=False,
                message=f"I don't have '{product_name}'. Available: {available_products}",
            )

        if product.stock_quantity == 0:
            message = f"Sorry, {product.name} is out of stock."
        else:
            message = f"{product.name}: {product.stock_quantity} units available at ${product.price:.2f} each"

        return AIResponse(success=True, message=message)

    def _find_product_by_name(self, name: str) -> Optional[Product]:
        name_lower = name.lower().strip()

        products = self.product_repo.search_by_name(name)
        if products:
            return products[0]

        aliases = {
            "coke": "Coca-Cola",
            "cola": "Coca-Cola",
            "cokes": "Coca-Cola",
            "fanta": "Fanta Orange",
            "guarana": "Guarana Antarctica",
            "sprite": "Sprite",
            "pepsi": "Pepsi",
        }

        for alias, real_name in aliases.items():
            if alias in name_lower:
                products = self.product_repo.search_by_name(real_name)
                if products:
                    return products[0]

        return None

    def _get_available_products_list(self) -> str:
        products = self.product_repo.get_available_products()
        return ", ".join([p.name for p in products]) if products else "none"
