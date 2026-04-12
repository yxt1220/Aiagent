from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = handle_chat(
        message=request.message,
        session_id=request.session_id,
        context=request.context or ""
    )
    return ChatResponse(**result)