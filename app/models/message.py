from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel, String


class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True, ondelete="CASCADE")
    role: Literal["system", "user", "assistant", "tool"] = Field(sa_column=Column(String(20), nullable=False))
    content: str = Field()
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
