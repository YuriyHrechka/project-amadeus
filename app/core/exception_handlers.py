from fastapi import Request
from fastapi.responses import JSONResponse

from app.adapters.base import LLMAuthenticationError, LLMError, LLMRateLimitError, LLMTimeoutError, LLMConnectionError


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
