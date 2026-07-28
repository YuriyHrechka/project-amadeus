from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """A single message in a conversation, in the role/content shape LLM providers expect."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMError(Exception):
    """Base exception for all LLM adapter errors."""


class LLMTimeoutError(LLMError):
    """Raised when a request to the LLM provider times out."""


class LLMRateLimitError(LLMError):
    """Raised when the LLM provider returns a rate-limit error."""


class LLMAuthenticationError(LLMError):
    """Raised when the LLM provider rejects the API key."""


class LLMAdapter(ABC):
    """Provider-agnostic interface for talking to an LLM.

    Concrete implementations (e.g. OpenAIAdapter) hide a specific provider's SDK
    behind this contract, so callers never depend on provider-specific types.
    """

    @abstractmethod
    async def generate(self, messages: list[ChatMessage]) -> str:
        """Generate a response from the language model.

        Args:
            messages: Ordered conversation history to send to the model.

        Returns:
            The model's response text.

        Raises:
            LLMTimeoutError: If the request to the provider times out.
            LLMRateLimitError: If the provider rate-limits the request.
            LLMAuthenticationError: If the provider rejects the credentials.
            LLMError: For any other provider-side failure.
        """
        pass
