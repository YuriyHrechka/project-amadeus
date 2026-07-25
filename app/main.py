from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.VERSION, description="Voice Assistant API", lifespan=lifespan
)


@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "message": "El Psy Kongroo",
        "version": settings.VERSION,
        "divergence_meter": settings.DIVERGENCE_METER,
    }
