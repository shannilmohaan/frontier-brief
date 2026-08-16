import logging
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import digest, refresh
from app.core.config import settings
from app.db.database import engine

# Ensure app.* loggers emit at INFO — uvicorn's dictConfig has disable_existing_loggers=False
# so this survives uvicorn's logging setup that runs after import.
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "plain",
        }
    },
    "formatters": {
        "plain": {"format": "%(levelname)s %(name)s: %(message)s"}
    },
    "loggers": {
        "app": {"handlers": ["stderr"], "level": "INFO", "propagate": False}
    },
})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(title="Frontier Brief API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-Refresh-Key"],
)

app.include_router(digest.router)
app.include_router(refresh.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
