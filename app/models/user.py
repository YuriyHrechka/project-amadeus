from uuid import UUID, uuid4
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from datetime import datetime


class BaseUser(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


class User(BaseUser, table=True):
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )
