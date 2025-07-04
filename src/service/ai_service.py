from src.model.purchase import PurchaseIntent, UserIntent
from src.core.ai_client import client
from src.core.prompts import PURCHASE_PROMPT


class AIService:
    def __init__(self):
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
