"""Shared pytest fixtures.

Must set dummy env vars before any `app.*` import — `Settings()` validates
them at import time. `setdefault` so real exported env vars still win.
"""

import os

os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("OPENAI__API_KEY", "sk-test-dummy-key")

from unittest.mock import AsyncMock  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.adapters.base import LLMAdapter  # noqa: E402
from app.adapters.dependencies import get_llm_adapter  # noqa: E402
from app.main import app  # noqa: E402
from app.models.conversation import Conversation  # noqa: E402
from app.services.conversation_service import ConversationService  # noqa: E402
from app.services.dependencies import get_conversation_service  # noqa: E402


@pytest.fixture
def mock_llm_adapter() -> AsyncMock:
    """A fake LLMAdapter whose `generate()` is an AsyncMock, for endpoint tests."""
    return AsyncMock(spec=LLMAdapter)


@pytest.fixture
def mock_conversation_service() -> AsyncMock:
    """A fake ConversationService for endpoint tests.

    `create_conversation`/`get_conversation` return a fixed, real `Conversation`
    (not a bare Mock) so `ChatResponse(conversation_id=conversation.id)` has a
    real UUID to validate against. `get_recent_messages` defaults to an empty
    history — override per-test if a case needs specific messages.
    """
    service = AsyncMock(spec=ConversationService)
    conversation = Conversation(id=uuid4(), user_id=uuid4())
    service.create_conversation.return_value = conversation
    service.get_conversation.return_value = conversation
    service.get_recent_messages.return_value = []
    return service


@pytest.fixture
def client(mock_llm_adapter: AsyncMock, mock_conversation_service: AsyncMock) -> TestClient:
    """TestClient with the LLM adapter and ConversationService swapped for mocks.

    Not used as a context manager, so `lifespan`'s Postgres check never runs.
    """
    app.dependency_overrides[get_llm_adapter] = lambda: mock_llm_adapter
    app.dependency_overrides[get_conversation_service] = lambda: mock_conversation_service
    yield TestClient(app)
    app.dependency_overrides.clear()
