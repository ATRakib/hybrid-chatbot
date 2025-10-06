from fastapi import APIRouter
from app.models.schemas import ChatMessage, ChatResponse
from app.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    response, sources = search_service.search_and_respond(message.message)
    return ChatResponse(response=response, sources=sources)