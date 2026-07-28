from app.adapters.base import LLMAdapter
from app.adapters.ollama_adapter import OllamaAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.core.config import settings

if settings.LLM_PROVIDER == "openai":
    _llm_adapter: LLMAdapter = OpenAIAdapter(settings.openai)
elif settings.LLM_PROVIDER == "ollama":
    _llm_adapter: LLMAdapter = OllamaAdapter(settings.ollama)
else:
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER!r}")


def get_llm_adapter() -> LLMAdapter:
    return _llm_adapter
