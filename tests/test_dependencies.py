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


def _run_and_get_adapter_class_name(llm_provider: str, extra_env: dict[str, str]) -> str:
    code = "from app.adapters.dependencies import get_llm_adapter; print(type(get_llm_adapter()).__name__)"
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
    return result.stdout.strip()


def test_factory_selects_openai_adapter() -> None:
    class_name = _run_and_get_adapter_class_name("openai", {"OPENAI__API_KEY": "sk-test"})
    assert class_name == "OpenAIAdapter"


def test_factory_selects_ollama_adapter() -> None:
    class_name = _run_and_get_adapter_class_name("ollama", {"OLLAMA__HOST": "http://localhost:11434"})
    assert class_name == "OllamaAdapter"
