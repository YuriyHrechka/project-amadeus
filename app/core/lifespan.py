from fastapi import FastAPI
from sqlalchemy import text
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.core.database import engine
from app.core.logger import init_logger

logger = init_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database connection check failed on startup")
        raise

    logger.info("Application startup complete")
    try:
        yield
    finally:
        logger.info("Application shutting down")
        await engine.dispose()
