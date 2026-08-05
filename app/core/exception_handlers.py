from fastapi import Request
from fastapi.responses import JSONResponse

from app.adapters.base import LLMAuthenticationError, LLMConnectionError, LLMError, LLMRateLimitError, LLMTimeoutError
from app.services.conversation_service import ConversationNotFoundError


async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    if isinstance(exc, LLMTimeoutError):
        status_code = 504
    elif isinstance(exc, LLMRateLimitError):
        status_code = 429
    elif isinstance(exc, LLMAuthenticationError):
        status_code = 500
    elif isinstance(exc, LLMConnectionError):
        status_code = 503
    else:
        status_code = 502

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


async def conversation_not_found_handler(request: Request, exc: ConversationNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
