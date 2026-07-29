"""Tests for the `get_llm_adapter` factory.

Runs in a subprocess per case, since `_llm_adapter` is a module-level
singleton built at import time — a fresh interpreter avoids leaking state
between tests.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_and_get_adapter_class_names(llm_provider: str, extra_env: dict[str, str]) -> tuple[str, str]:
    """Returns (outer_class_name, inner_class_name) for the adapter the factory builds.

    The factory now always wraps the provider adapter in `RetryingLLMAdapter`,
    so `get_llm_adapter()` itself is never the provider class directly.
    """
    code = (
        "from app.adapters.dependencies import get_llm_adapter; "
        "adapter = get_llm_adapter(); "
        "print(type(adapter).__name__); "
        "print(type(adapter.inner_adapter).__name__)"
    )
    env = {
        **os.environ,
        "DB_USER": "test",
        "DB_PASSWORD": "test",
        "DB_HOST": "localhost",
        "DB_NAME": "test",
        "LLM_PROVIDER": llm_provider,
        **extra_env,
    }
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"subprocess failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    outer_name, inner_name = result.stdout.strip().splitlines()
    return outer_name, inner_name


def test_factory_selects_openai_adapter() -> None:
    outer_name, inner_name = _run_and_get_adapter_class_names("openai", {"OPENAI__API_KEY": "sk-test"})
    assert outer_name == "RetryingLLMAdapter"
    assert inner_name == "OpenAIAdapter"


def test_factory_selects_ollama_adapter() -> None:
    outer_name, inner_name = _run_and_get_adapter_class_names("ollama", {"OLLAMA__HOST": "http://localhost:11434"})
    assert outer_name == "RetryingLLMAdapter"
    assert inner_name == "OllamaAdapter"
