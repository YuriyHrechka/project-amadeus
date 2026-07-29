import httpx

from app.adapters.base import (
    ChatMessage,
    LLMAdapter,
    LLMConnectionError,
    LLMError,
    LLMTimeoutError,
)
from app.core.llm_config import OllamaSettings
from app.core.logger import init_logger

logger = init_logger(__name__)


class OllamaAdapter(LLMAdapter):
    """LLMAdapter implementation backed by Ollama API."""

    def __init__(self, settings: OllamaSettings):
        self.settings = settings
        self.client = httpx.AsyncClient(base_url=settings.host, timeout=settings.timeout_seconds)

    async def generate(self, messages: list[ChatMessage]) -> str:
        try:
            payload = {
                "model": self.settings.model,
                "messages": [m.model_dump() for m in messages],
                "stream": False,
                "think": self.settings.think,
            }
            response = await self.client.post("api/chat", json=payload)
            response.raise_for_status()
        except httpx.ConnectError as e:
            raise LLMConnectionError("Could not connect to Ollama — is it running?") from e
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(f"Ollama request timed out after {self.settings.timeout_seconds}s") from e
        except httpx.HTTPStatusError as e:
            raise LLMError(f"Ollama returned an error: {e}") from e
        except httpx.HTTPError as e:
            raise LLMError(f"Unexpected Ollama error: {e}") from e

        data = response.json()
        logger.info(
            "generate() completed: model=%s prompt_tokens=%d completion_tokens=%d total_tokens=%d",
            self.settings.model,
            data["prompt_eval_count"],
            data["eval_count"],
            data["prompt_eval_count"] + data["eval_count"],
        )

        return data["message"]["content"]
