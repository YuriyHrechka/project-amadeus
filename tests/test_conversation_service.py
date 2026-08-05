"""Tests for ConversationService, against a real (in-memory SQLite) database.

Unlike the endpoint tests, this deliberately does NOT mock the session — the
whole point is to verify the actual SQL behavior (filtering, ownership check,
sliding-window ordering), not just that methods were called.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.base import ChatMessage
from app.models.message import Message
from app.services.conversation_service import ConversationNotFoundError, ConversationService


@pytest.fixture
async def session():
    """A fresh in-memory SQLite database per test, with all tables created.

    `StaticPool` keeps one connection alive for the engine's lifetime —
    without it, every checkout would get its own empty `:memory:` database.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def service(session: AsyncSession) -> ConversationService:
    return ConversationService(session)


async def _insert_message_at(
    session: AsyncSession, conversation_id, role: str, content: str, created_at: datetime
) -> Message:
    """Insert a Message with an explicit `created_at`, bypassing `add_message`.

    `add_message` always lets the DB stamp `created_at` via `now()`, so it
    can't produce messages with controlled, distinct timestamps. Ordering
    tests need that control to be deterministic — real inserts a few
    milliseconds apart aren't reliable here, since SQLite's `CURRENT_TIMESTAMP`
    only has one-second resolution.
    """
    message = Message(conversation_id=conversation_id, role=role, content=content, created_at=created_at)
    session.add(message)
    await session.commit()
    return message


async def test_create_conversation_persists_and_returns_conversation(service: ConversationService) -> None:
    user_id = uuid4()

    conversation = await service.create_conversation(user_id=user_id)

    assert conversation.id is not None
    assert conversation.user_id == user_id
    assert conversation.created_at is not None


async def test_get_conversation_returns_existing(service: ConversationService) -> None:
    user_id = uuid4()
    created = await service.create_conversation(user_id=user_id)

    fetched = await service.get_conversation(user_id=user_id, conversation_id=created.id)

    assert fetched.id == created.id


async def test_get_conversation_raises_when_not_found(service: ConversationService) -> None:
    with pytest.raises(ConversationNotFoundError):
        await service.get_conversation(user_id=uuid4(), conversation_id=uuid4())


async def test_get_conversation_raises_when_not_owned_by_user(service: ConversationService) -> None:
    """A conversation that exists but belongs to someone else must look identical to 'not found'."""
    owner_id = uuid4()
    created = await service.create_conversation(user_id=owner_id)

    with pytest.raises(ConversationNotFoundError):
        await service.get_conversation(user_id=uuid4(), conversation_id=created.id)


async def test_add_message_persists_and_returns_message(service: ConversationService) -> None:
    conversation = await service.create_conversation(user_id=uuid4())

    message = await service.add_message(conversation.id, ChatMessage(role="user", content="hello"))

    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == "hello"


async def test_get_recent_messages_returns_chronological_order(
    service: ConversationService, session: AsyncSession
) -> None:
    conversation = await service.create_conversation(user_id=uuid4())
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    await _insert_message_at(session, conversation.id, "user", "first", base_time)
    await _insert_message_at(session, conversation.id, "assistant", "second", base_time + timedelta(seconds=1))
    await _insert_message_at(session, conversation.id, "user", "third", base_time + timedelta(seconds=2))

    history = await service.get_recent_messages(conversation.id)

    assert [m.content for m in history] == ["first", "second", "third"]
    assert [m.role for m in history] == ["user", "assistant", "user"]
    assert all(isinstance(m, ChatMessage) for m in history)


async def test_get_recent_messages_respects_limit_and_keeps_newest(
    service: ConversationService, session: AsyncSession
) -> None:
    conversation = await service.create_conversation(user_id=uuid4())
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(5):
        await _insert_message_at(session, conversation.id, "user", f"message {i}", base_time + timedelta(seconds=i))

    history = await service.get_recent_messages(conversation.id, limit=2)

    # Newest 2 of 5, still returned oldest-first (not reversed twice).
    assert [m.content for m in history] == ["message 3", "message 4"]


async def test_get_recent_messages_only_returns_messages_for_that_conversation(
    service: ConversationService, session: AsyncSession
) -> None:
    conversation_a = await service.create_conversation(user_id=uuid4())
    conversation_b = await service.create_conversation(user_id=uuid4())
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    await _insert_message_at(session, conversation_a.id, "user", "in A", base_time)
    await _insert_message_at(session, conversation_b.id, "user", "in B", base_time)

    history = await service.get_recent_messages(conversation_a.id)

    assert [m.content for m in history] == ["in A"]
