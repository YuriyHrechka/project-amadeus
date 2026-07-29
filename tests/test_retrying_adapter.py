"""Unit tests for RetryingLLMAdapter.

Wraps a fake `LLMAdapter` (AsyncMock), so these tests exercise only the
retry/no-retry decision and the tenacity wiring, not any real provider.
`asyncio.sleep` is patched everywhere so retries don't slow down the suite
with real exponential backoff.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.adapters.base import (
    ChatMessage,
    LLMAdapter,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMTimeoutError,
)
from app.adapters.retrying_adapter import RetryingLLMAdapter


@pytest.fixture(autouse=True)
def _no_real_sleep():
    """Without this, a retrying test would wait for real exponential backoff."""
    with patch("asyncio.sleep", new=AsyncMock()):
        yield


@pytest.fixture
def inner_adapter() -> AsyncMock:
    return AsyncMock(spec=LLMAdapter)


async def test_generate_succeeds_on_first_attempt(inner_adapter: AsyncMock) -> None:
    inner_adapter.generate.return_value = "hello"
    adapter = RetryingLLMAdapter(inner_adapter, max_retries=3)

    result = await adapter.generate([ChatMessage(role="user", content="hi")])

    assert result == "hello"
    assert inner_adapter.generate.await_count == 1


async def test_generate_retries_then_succeeds(inner_adapter: AsyncMock) -> None:
    inner_adapter.generate.side_effect = [LLMTimeoutError("a"), LLMConnectionError("b"), "hello"]
    adapter = RetryingLLMAdapter(inner_adapter, max_retries=5)

    result = await adapter.generate([ChatMessage(role="user", content="hi")])

    assert result == "hello"
    assert inner_adapter.generate.await_count == 3


async def test_generate_reraises_original_error_after_exhausting_retries(inner_adapter: AsyncMock) -> None:
    original = LLMTimeoutError("always fails")
    inner_adapter.generate.side_effect = original
    adapter = RetryingLLMAdapter(inner_adapter, max_retries=3)

    with pytest.raises(LLMTimeoutError) as exc_info:
        await adapter.generate([ChatMessage(role="user", content="hi")])

    assert exc_info.value is original
    assert inner_adapter.generate.await_count == 3


async def test_generate_does_not_retry_authentication_error(inner_adapter: AsyncMock) -> None:
    """Auth errors won't fix themselves on a retry, so only one attempt should happen."""
    inner_adapter.generate.side_effect = LLMAuthenticationError("bad key")
    adapter = RetryingLLMAdapter(inner_adapter, max_retries=5)

    with pytest.raises(LLMAuthenticationError):
        await adapter.generate([ChatMessage(role="user", content="hi")])

    assert inner_adapter.generate.await_count == 1


async def test_generate_does_not_retry_generic_llm_error(inner_adapter: AsyncMock) -> None:
    """Unclassified LLMError isn't known to be transient, so it's not retried either."""
    inner_adapter.generate.side_effect = LLMError("unexpected")
    adapter = RetryingLLMAdapter(inner_adapter, max_retries=5)

    with pytest.raises(LLMError):
        await adapter.generate([ChatMessage(role="user", content="hi")])

    assert inner_adapter.generate.await_count == 1
