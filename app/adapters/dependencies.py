from app.adapters.base import LLMAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.core.config import settings

if settings.LLM_PROVIDER == "openai":
    _llm_adapter: LLMAdapter = OpenAIAdapter(settings.openai)
else:
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER!r}")


def get_llm_adapter() -> LLMAdapter:
    return _llm_adapter
