from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.db.database import get_session
from src.service.ai_service import AIService
from src.service.purchase_service import PurchaseService
from src.model.ai import AIResponse, ChatRequest

router = APIRouter(tags=["vending-machine"])


@router.post("/chat", response_model=AIResponse)
def chat_with_vending_machine(
    request: ChatRequest, session: Session = Depends(get_session)
):
    try:
        ai_service = AIService()
        purchase_service = PurchaseService(session)
        intent = ai_service.parse_user_message(request.message)
        response = purchase_service.process_purchase(intent, request.message)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Sorry, I'm having trouble right now. Please try again in a moment.",
        )


@router.get("/health")
def health_check():
    return {"status": "operational", "message": "Vending machine ready to serve!"}
