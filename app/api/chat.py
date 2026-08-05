from fastapi import APIRouter

from app.adapters.base import ChatMessage
from app.adapters.dependencies import LLMAdapterDep
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.dependencies import ConversationServiceDep

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, llm: LLMAdapterDep, service: ConversationServiceDep) -> ChatResponse:
    """Save the user's message, ask the configured LLM for a reply, and save that too.

    Continues an existing conversation if `request.conversation_id` is set,
    otherwise starts a new one. The LLM sees the conversation's recent history
    via `ConversationService.get_recent_messages` plus the new message, so it
    can respond with the prior context in mind.

    Args:
        request: The user's message, plus optional `conversation_id` (omit to
            start a new conversation) and `user_id` (temporary, until auth exists).
        llm: LLM adapter selected via `LLMAdapterDep`, based on LLM_PROVIDER.
        service: Conversation persistence, injected via `ConversationServiceDep`.

    Returns:
        The model's reply and the conversation's id, wrapped in a ChatResponse.

    Raises:
        ConversationNotFoundError: If `conversation_id` is given but no such
            conversation exists for this `user_id`.
    """
    if request.conversation_id:
        conversation = await service.get_conversation(user_id=request.user_id, conversation_id=request.conversation_id)
    else:
        conversation = await service.create_conversation(user_id=request.user_id)

    await service.add_message(
        conversation_id=conversation.id, message=ChatMessage(role="user", content=request.message)
    )

    recent_messages = await service.get_recent_messages(conversation.id)

    result = await llm.generate(recent_messages)

    await service.add_message(conversation_id=conversation.id, message=ChatMessage(role="assistant", content=result))
    return ChatResponse(text=result, conversation_id=conversation.id)
