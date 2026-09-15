"""Chatbot API Routes"""
from fastapi import APIRouter
from backend.app.schemas.schemas import ChatInput
from backend.app.state import chatbot_service, iot_simulator

router = APIRouter()

@router.post("/chat")
async def chat(data: ChatInput):
    """Send a message to the AI diagnostic chatbot."""
    context = {}
    if data.device_id:
        context["device_id"] = data.device_id
        status = iot_simulator.get_device_status(data.device_id)
        if status and status.get("latest_reading"):
            context["readings"] = status["latest_reading"]
    response = chatbot_service.chat(data.message, context=context)
    return response.to_dict()

@router.get("/chat/history")
async def get_chat_history(limit: int = 20):
    """Get conversation history."""
    return chatbot_service.get_history(limit=limit)

@router.post("/chat/clear")
async def clear_chat():
    """Clear conversation history."""
    chatbot_service.clear_history()
    return {"status": "cleared"}
