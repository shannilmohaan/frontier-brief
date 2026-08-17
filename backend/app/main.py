import logging
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import update

from app.api import digest, refresh
from app.core.config import settings
from app.db.database import AsyncSessionLocal, engine
from app.db.models import DigestCycle

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


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Mark any cycles stuck in "running" or "pending" as failed — they were
    # orphaned by a previous container restart and will block future refreshes.
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(DigestCycle)
                .where(DigestCycle.status.in_(["running", "pending"]))
                .values(status="failed", error_message="Server restarted — cycle orphaned")
            )
            if result.rowcount:
                logger.warning("Marked %d orphaned cycle(s) as failed on startup", result.rowcount)
            await session.commit()
    except Exception:
        logger.exception("Could not clean up orphaned cycles on startup")

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
