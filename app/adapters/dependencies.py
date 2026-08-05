from typing import Annotated

from fastapi import Depends

from app.adapters.base import LLMAdapter
from app.adapters.ollama_adapter import OllamaAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.adapters.retrying_adapter import RetryingLLMAdapter
from app.core.config import settings

if settings.LLM_PROVIDER == "openai":
    _raw_adapter: LLMAdapter = OpenAIAdapter(settings.openai)
    _max_retries: int = settings.openai.max_retries
elif settings.LLM_PROVIDER == "ollama":
    _raw_adapter: LLMAdapter = OllamaAdapter(settings.ollama)
    _max_retries: int = settings.ollama.max_retries
else:
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER!r}")

_llm_adapter = RetryingLLMAdapter(_raw_adapter, _max_retries)


def get_llm_adapter() -> LLMAdapter:
    return _llm_adapter


LLMAdapterDep = Annotated[LLMAdapter, Depends(get_llm_adapter)]
