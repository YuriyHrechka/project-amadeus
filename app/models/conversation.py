from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class BaseConversation(SQLModel):
    title: Optional[str] = Field(default=None)


class Conversation(BaseConversation, table=True):
    __tablename__ = "conversation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )

    user: "User" = Relationship(back_populates="conversations")
