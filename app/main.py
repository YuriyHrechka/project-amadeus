from fastapi import FastAPI

from app.adapters.base import LLMError
from app.api.chat import router as chat_router
from app.core.config import settings
from app.core.exception_handlers import llm_error_handler
from app.core.lifespan import lifespan

app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.VERSION, description="Voice Assistant API", lifespan=lifespan
)

app.add_exception_handler(LLMError, llm_error_handler)

app.include_router(chat_router)


@app.get("/ping")
async def ping():
    provider_settings = getattr(settings, settings.LLM_PROVIDER)
    return {
        "status": "ok",
        "message": "El Psy Kongroo",
        "version": settings.VERSION,
        "divergence_meter": settings.DIVERGENCE_METER,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": provider_settings.model,
    }
