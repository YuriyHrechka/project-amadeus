import openai
from openai import AsyncOpenAI

from app.core.llm_config import OpenAISettings
from app.core.logger import init_logger
from app.adapters.base import (
    LLMAdapter,
    ChatMessage,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMError,
)

logger = init_logger("OpenAIAdapter")


class OpenAIAdapter(LLMAdapter):
    """LLMAdapter implementation backed by OpenAI's Chat Completions API."""

    def __init__(self, settings: OpenAISettings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.api_key.get_secret_value())
        self.model = settings.model

    async def generate(self, messages: list[ChatMessage]) -> str:
        """Call OpenAI's chat.completions API and return the generated text.

        Provider-specific exceptions from the openai SDK are translated into
        the LLMError hierarchy defined in `base.py` — see LLMAdapter.generate
        for the full list of exceptions this can raise.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=[m.model_dump() for m in messages], timeout=self.settings.timeout_seconds
            )
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"OpenAI request timed out after {self.settings.timeout_seconds}s") from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError("OpenAI rate limit exceeded — retry after a short delay") from e
        except openai.AuthenticationError as e:
            raise LLMAuthenticationError("OpenAI rejected the API key — check OPENAI__API_KEY in your .env file") from e
        except openai.APIError as e:
            raise LLMError(f"Unexpected OpenAI API error: {e}") from e

        logger.info(
            "generate() completed: model=%s prompt_tokens=%d completion_tokens=%d total_tokens=%d",
            self.model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
            response.usage.total_tokens,
        )
        return response.choices[0].message.content
