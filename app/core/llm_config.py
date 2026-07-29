from pydantic import BaseModel, SecretStr


class BaseLLMSettings(BaseModel):
    """Fields shared by every provider-specific LLM settings class."""

    timeout_seconds: float = 30
    max_retries: int = 3


class OpenAISettings(BaseLLMSettings):
    """Configuration for the OpenAI provider."""

    api_key: SecretStr
    model: str = "gpt-5.4-mini"


class OllamaSettings(BaseLLMSettings):
    """Configuration for the Ollama provider."""

    host: str = "http://localhost:11434"
    model: str = "qwen3.5:4b"
    # Thinking mode adds a slow internal reasoning trace before the reply.
    think: bool = False
