from sqlmodel import Session
from typing import Optional

from src.db.repository.product_repository import ProductRepository
from src.db.repository.transaction_repository import TransactionRepository
from src.model.transaction import (
    TransactionCreate,
    TransactionStatus,
)
from src.model.purchase import PurchaseIntent, UserIntent, AIResponse
from src.model.product import Product
from src.core.ai_client import client
from src.core.prompts import PURCHASE_PROMPT


class PurchaseService:
    def __init__(self, session: Session = None):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.client = client

    def parse_user_message(self, user_message: str) -> PurchaseIntent:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=PurchaseIntent,
                messages=[
                    {"role": "system", "content": PURCHASE_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
            )
            return response

        except Exception as e:
            return PurchaseIntent(
                intent=UserIntent.UNKNOWN,
                product_name=None,
                quantity=None,
                confidence=0.0,
            )

    def process_purchase(self, intent: PurchaseIntent, user_message: str) -> AIResponse:
        if intent.intent != UserIntent.PURCHASE:
            return self._handle_non_purchase_intent(intent)

        if not intent.product_name or not intent.quantity:
            return AIResponse(
                success=False,
                message="Please specify which product and how many you want. For example: 'I want 2 cokes'",
                purchase_intent=intent,
            )

        product = self._find_product_by_name(intent.product_name)
        if not product:
            available_products = self._get_available_products_list()
            return AIResponse(
                success=False,
                message=f"Sorry, I don't have '{intent.product_name}'. Available products: {available_products}",
                purchase_intent=intent,
            )

        if product.stock_quantity < intent.quantity:
            return AIResponse(
                success=False,
                message=f"Sorry, we only have {product.stock_quantity} {product.name} in stock.",
                purchase_intent=intent,
            )

        unit_price = product.price
        print(
            f"DEBUG: Product '{product.name}' found with price: {unit_price} (type: {type(unit_price)})"
        )

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
                    success=False,
                    message="Transaction failed due to a stock issue. Please try again.",
                    purchase_intent=intent,
                )

            transaction.status = TransactionStatus.SUCCESS
            self.session.commit()

            return AIResponse(
                success=True,
                message=f"Great! I've dispensed {intent.quantity} {product.name} for ${total_price:.2f}. Enjoy your drink!",
                purchase_intent=intent,
                transaction_id=transaction.id,
                total_price=float(total_price),
            )

        except Exception as e:
            return AIResponse(
                success=False,
                message="Sorry, a critical error occurred with your purchase. Please try again.",
                purchase_intent=intent,
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
                    purchase_intent=intent,
                )

        else:
            return AIResponse(
                success=True,
                message="I'm a soda vending machine! You can:\n Buy products: 'I want 2 cokes'\n Check inventory: 'What do you have?'\n Check stock: 'How many sprites are left?'",
                purchase_intent=intent,
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
