"""Unit tests for OllamaAdapter.

Mocks `adapter.client.post` and raises real `httpx` exception classes, so
the `except` clauses are actually exercised.
"""

from unittest.mock import AsyncMock

import httpx
import pytest

from app.adapters.base import ChatMessage, LLMConnectionError, LLMError, LLMTimeoutError
from app.adapters.ollama_adapter import OllamaAdapter
from app.core.llm_config import OllamaSettings


@pytest.fixture
def adapter() -> OllamaAdapter:
    return OllamaAdapter(OllamaSettings(host="http://localhost:11434"))


def _fake_request() -> httpx.Request:
    return httpx.Request("POST", "http://localhost:11434/api/chat")


def _fake_response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code=status_code, request=_fake_request())


def _ok_response() -> httpx.Response:
    """A 200 response with a body shaped like Ollama's real /api/chat response."""
    return httpx.Response(
        status_code=200,
        request=_fake_request(),
        json={
            "message": {"role": "assistant", "content": "Hello there"},
            "prompt_eval_count": 10,
            "eval_count": 5,
        },
    )


async def test_generate_returns_model_text(adapter: OllamaAdapter) -> None:
    adapter.client.post = AsyncMock(return_value=_ok_response())

    result = await adapter.generate([ChatMessage(role="user", content="hi")])

    assert result == "Hello there"
    adapter.client.post.assert_awaited_once()


async def test_generate_raises_llm_connection_error(adapter: OllamaAdapter) -> None:
    adapter.client.post = AsyncMock(side_effect=httpx.ConnectError("connection refused", request=_fake_request()))

    with pytest.raises(LLMConnectionError):
        await adapter.generate([ChatMessage(role="user", content="hi")])


async def test_generate_raises_llm_timeout_error(adapter: OllamaAdapter) -> None:
    adapter.client.post = AsyncMock(side_effect=httpx.TimeoutException("timed out", request=_fake_request()))

    with pytest.raises(LLMTimeoutError):
        await adapter.generate([ChatMessage(role="user", content="hi")])


async def test_generate_raises_llm_error_for_http_status_error(adapter: OllamaAdapter) -> None:
    error_response = _fake_response(500)
    adapter.client.post = AsyncMock(return_value=error_response)

    with pytest.raises(LLMError):
        await adapter.generate([ChatMessage(role="user", content="hi")])


async def test_generate_preserves_exception_chain(adapter: OllamaAdapter) -> None:
    original = httpx.ConnectError("connection refused", request=_fake_request())
    adapter.client.post = AsyncMock(side_effect=original)

    with pytest.raises(LLMConnectionError) as exc_info:
        await adapter.generate([ChatMessage(role="user", content="hi")])

    assert exc_info.value.__cause__ is original
