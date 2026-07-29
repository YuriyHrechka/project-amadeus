import logging

from tenacity import AsyncRetrying, before_sleep_log, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.adapters.base import ChatMessage, LLMAdapter, LLMConnectionError, LLMRateLimitError, LLMTimeoutError
from app.core.logger import init_logger

logger = init_logger(__name__)


class RetryingLLMAdapter(LLMAdapter):
    """Wraps another LLMAdapter and retries transient failures.

    Retries only transient errors — timeouts, connection issues, rate limits.
    Auth errors and other unclassified LLMError failures are not retried,
    since retrying them would just waste time reproducing the same failure.
    """

    def __init__(self, inner_adapter: LLMAdapter, max_retries: int):
        self.inner_adapter = inner_adapter
        self.max_retries = max_retries

    async def generate(self, messages: list[ChatMessage]) -> str:
        """Call the wrapped adapter's `generate`, retrying on transient errors.

        Raises:
            LLMError: The original exception from the wrapped adapter, once
                retries are exhausted (or immediately, if not retryable).
        """
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            retry=retry_if_exception_type((LLMTimeoutError, LLMConnectionError, LLMRateLimitError)),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        ):
            with attempt:
                return await self.inner_adapter.generate(messages)
