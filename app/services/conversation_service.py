from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.base import ChatMessage
from app.core.logger import init_logger
from app.models.conversation import Conversation
from app.models.message import Message

logger = init_logger(__name__)
DEFAULT_HISTORY_LIMIT = 20


class ConversationNotFoundError(Exception):
    """Raised when a conversation doesn't exist, or isn't owned by the given user."""


class ConversationService:
    """Persistence layer for conversations and messages.

    Sits between the `/chat` endpoint and the database — callers only deal in
    `Conversation`/`Message`/`ChatMessage`, never in raw SQLModel sessions or
    queries. This is also the only place that knows how conversation history
    is windowed for the LLM (see `get_recent_messages`).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_conversation(self, user_id: UUID, conversation_id: UUID) -> Conversation:
        """Fetch an existing conversation owned by `user_id`.

        Raises:
            ConversationNotFoundError: If no conversation with this id exists,
                or it exists but isn't owned by `user_id`. Both cases return
                the same error so callers can't use this to probe which ids exist.
        """
        statement = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        result = await self.session.exec(statement=statement)
        conversation = result.one_or_none()
        if conversation is None:
            logger.info("Conversation %s not found for user %s", conversation_id, user_id)
            raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
        return conversation

    async def create_conversation(self, user_id: UUID, title: Optional[str] = None) -> Conversation:
        """Create and persist a brand new conversation for `user_id`."""
        conversation = Conversation(user_id=user_id, title=title)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_recent_messages(self, conversation_id: UUID, limit: int = DEFAULT_HISTORY_LIMIT) -> list[ChatMessage]:
        """Return up to `limit` most recent messages, oldest first, as ChatMessages.

        This is the sliding-window context sent to the LLM — messages are
        fetched newest-first (so `LIMIT` keeps the *most recent* ones), then
        reversed back into chronological order before returning.
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.exec(statement=statement)
        messages = result.all()

        chat_messages = [ChatMessage(role=msg.role, content=msg.content) for msg in reversed(messages)]
        return chat_messages

    async def add_message(self, conversation_id: UUID, message: ChatMessage) -> Message:
        """Persist a single message (user or assistant) to a conversation."""
        new_message = Message(conversation_id=conversation_id, role=message.role, content=message.content)
        self.session.add(new_message)
        await self.session.commit()
        return new_message
