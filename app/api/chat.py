from fastapi import APIRouter, Depends

from app.adapters.base import ChatMessage, LLMAdapter
from app.adapters.dependencies import get_llm_adapter
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, llm: LLMAdapter = Depends(get_llm_adapter)) -> ChatResponse:
    """Generate a chat response from the configured LLM provider.

    Args:
        request: The user's chat message.
        llm: LLM adapter selected via `get_llm_adapter`, based on LLM_PROVIDER.

    Returns:
        The model's reply wrapped in a ChatResponse.
    """
    message = ChatMessage(role="user", content=request.message)
    response_text = await llm.generate([message])
    return ChatResponse(text=response_text)
