"""Integration tests for POST /chat and GET /ping.

Uses the `client`/`mock_llm_adapter`/`mock_conversation_service` fixtures from
conftest.py, which override `get_llm_adapter` and `get_conversation_service` so
no real LLM provider or database is ever touched.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.adapters.base import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)

# Any well-formed UUID works — ConversationService is mocked, so nothing ever
# looks this up against a real user.
TEST_USER_ID = str(uuid4())


def test_ping(client: TestClient) -> None:
    response = client.get("/ping")
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["llm_provider"] == "openai"
    assert body["llm_model"]


def test_chat_success(client: TestClient, mock_llm_adapter: AsyncMock) -> None:
    mock_llm_adapter.generate.return_value = "Hello, human."

    response = client.post("/chat", json={"message": "hi", "user_id": TEST_USER_ID})
    body = response.json()

    assert response.status_code == 200
    assert body["text"] == "Hello, human."
    assert "conversation_id" in body
    mock_llm_adapter.generate.assert_awaited_once()


def test_chat_empty_message_is_rejected(client: TestClient) -> None:
    response = client.post("/chat", json={"message": "", "user_id": TEST_USER_ID})

    assert response.status_code == 422


def test_chat_whitespace_only_message_is_rejected(client: TestClient) -> None:
    """`str_strip_whitespace=True` strips first, so " " becomes "" and fails min_length."""
    response = client.post("/chat", json={"message": "   ", "user_id": TEST_USER_ID})

    assert response.status_code == 422


def test_chat_too_long_message_is_rejected(client: TestClient) -> None:
    response = client.post("/chat", json={"message": "x" * 2001, "user_id": TEST_USER_ID})

    assert response.status_code == 422


def test_chat_missing_message_field_is_rejected(client: TestClient) -> None:
    response = client.post("/chat", json={"user_id": TEST_USER_ID})

    assert response.status_code == 422


def test_chat_missing_user_id_is_rejected(client: TestClient) -> None:
    """`user_id` is required until real authentication exists."""
    response = client.post("/chat", json={"message": "hi"})

    assert response.status_code == 422


class TestErrorStatusCodeMapping:
    """Each LLMError subtype raised by the adapter should map to its documented HTTP status."""

    def test_timeout_maps_to_504(self, client: TestClient, mock_llm_adapter: AsyncMock) -> None:
        mock_llm_adapter.generate.side_effect = LLMTimeoutError("timed out")

        response = client.post("/chat", json={"message": "hi", "user_id": TEST_USER_ID})

        assert response.status_code == 504
        assert response.json() == {"detail": "timed out"}

    def test_rate_limit_maps_to_429(self, client: TestClient, mock_llm_adapter: AsyncMock) -> None:
        mock_llm_adapter.generate.side_effect = LLMRateLimitError("rate limited")

        response = client.post("/chat", json={"message": "hi", "user_id": TEST_USER_ID})

        assert response.status_code == 429

    def test_authentication_error_maps_to_500(self, client: TestClient, mock_llm_adapter: AsyncMock) -> None:
        mock_llm_adapter.generate.side_effect = LLMAuthenticationError("bad key")

        response = client.post("/chat", json={"message": "hi", "user_id": TEST_USER_ID})

        assert response.status_code == 500

    def test_connection_error_maps_to_503(self, client: TestClient, mock_llm_adapter: AsyncMock) -> None:
        mock_llm_adapter.generate.side_effect = LLMConnectionError("could not connect")

        response = client.post("/chat", json={"message": "hi", "user_id": TEST_USER_ID})

        assert response.status_code == 503

    def test_generic_llm_error_maps_to_502(self, client: TestClient, mock_llm_adapter: AsyncMock) -> None:
        mock_llm_adapter.generate.side_effect = LLMError("something unexpected")

        response = client.post("/chat", json={"message": "hi", "user_id": TEST_USER_ID})

        assert response.status_code == 502
