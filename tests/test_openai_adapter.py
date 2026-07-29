"""Unit tests for OpenAIAdapter.

Mocks `adapter.client.chat.completions.create` and raises real `openai`
exception classes, so the `except` clauses are actually exercised.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import openai
import pytest

from app.adapters.base import (
    ChatMessage,
    LLMAuthenticationError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.adapters.openai_adapter import OpenAIAdapter
from app.core.llm_config import OpenAISettings


@pytest.fixture
def adapter() -> OpenAIAdapter:
    return OpenAIAdapter(OpenAISettings(api_key="sk-test-dummy-key"))


def _fake_request() -> httpx.Request:
    return httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


def _fake_response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code=status_code, request=_fake_request())


async def test_generate_returns_model_text(adapter: OpenAIAdapter) -> None:
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Hello there"))],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )
    adapter.client.chat.completions.create = AsyncMock(return_value=fake_response)

    result = await adapter.generate([ChatMessage(role="user", content="hi")])

    assert result == "Hello there"
    adapter.client.chat.completions.create.assert_awaited_once()


async def test_generate_raises_llm_timeout_error(adapter: OpenAIAdapter) -> None:
    adapter.client.chat.completions.create = AsyncMock(side_effect=openai.APITimeoutError(request=_fake_request()))

    with pytest.raises(LLMTimeoutError):
        await adapter.generate([ChatMessage(role="user", content="hi")])


async def test_generate_raises_llm_rate_limit_error(adapter: OpenAIAdapter) -> None:
    adapter.client.chat.completions.create = AsyncMock(
        side_effect=openai.RateLimitError("rate limited", response=_fake_response(429), body=None)
    )

    with pytest.raises(LLMRateLimitError):
        await adapter.generate([ChatMessage(role="user", content="hi")])


async def test_generate_raises_llm_authentication_error(adapter: OpenAIAdapter) -> None:
    adapter.client.chat.completions.create = AsyncMock(
        side_effect=openai.AuthenticationError("bad key", response=_fake_response(401), body=None)
    )

    with pytest.raises(LLMAuthenticationError):
        await adapter.generate([ChatMessage(role="user", content="hi")])


async def test_generate_raises_llm_error_for_other_api_errors(adapter: OpenAIAdapter) -> None:
    adapter.client.chat.completions.create = AsyncMock(
        side_effect=openai.APIError("something broke", request=_fake_request(), body=None)
    )

    with pytest.raises(LLMError):
        await adapter.generate([ChatMessage(role="user", content="hi")])


async def test_generate_preserves_exception_chain(adapter: OpenAIAdapter) -> None:
    """Our custom exceptions should be raised `from` the original SDK exception."""
    original = openai.APITimeoutError(request=_fake_request())
    adapter.client.chat.completions.create = AsyncMock(side_effect=original)

    with pytest.raises(LLMTimeoutError) as exc_info:
        await adapter.generate([ChatMessage(role="user", content="hi")])

    assert exc_info.value.__cause__ is original
