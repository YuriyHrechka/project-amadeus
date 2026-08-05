from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_db
from app.services.conversation_service import ConversationService


def get_conversation_service(session: AsyncSession = Depends(get_db)) -> ConversationService:
    return ConversationService(session=session)


ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]
