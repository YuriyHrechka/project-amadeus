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

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.adapters.base import LLMAdapter  # noqa: E402
from app.adapters.dependencies import get_llm_adapter  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def mock_llm_adapter() -> AsyncMock:
    """A fake LLMAdapter whose `generate()` is an AsyncMock, for endpoint tests."""
    return AsyncMock(spec=LLMAdapter)


@pytest.fixture
def client(mock_llm_adapter: AsyncMock) -> TestClient:
    """TestClient with the LLM adapter swapped for `mock_llm_adapter`.

    Not used as a context manager, so `lifespan`'s Postgres check never runs.
    """
    app.dependency_overrides[get_llm_adapter] = lambda: mock_llm_adapter
    yield TestClient(app)
    app.dependency_overrides.clear()
