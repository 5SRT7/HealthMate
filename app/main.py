"""HealthMate 应用入口。"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.chat import router as chat_router
from app.api.profile import router as profile_router
from app.api.archive import router as archive_router
from app.api.voice import router as voice_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import init_db

setup_logging()
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Preload ASR model in background so first voice call is instant
    import threading

    def _preload_asr():
        try:
            from app.voice.asr import get_asr_model

            get_asr_model()
            logger.info("ASR model ready")
        except Exception as exc:
            logger.warning("ASR model preload skipped: %s", exc)

    threading.Thread(target=_preload_asr, daemon=True).start()
    models = list(settings.configured_models.keys())
    logger.info("HealthMate started | default=%s models=%s", settings.LLM_PROVIDER.value, models)
    yield
    logger.info("HealthMate shutdown")


app = FastAPI(
    title="HealthMate Agent API",
    version="0.2.0",
    description="Personal Healthcare AI Agent — Multi-Agent",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(chat_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(archive_router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")


@app.get("/")
async def serve_frontend() -> FileResponse:
    resp = FileResponse(STATIC_DIR / "index.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
