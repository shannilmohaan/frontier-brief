import hmac
import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import AsyncSessionLocal, get_session
from app.db.models import DigestCycle
from app.services.scheduler.pipeline import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/refresh", tags=["refresh"])


class RefreshAcceptedResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    created: bool


class RefreshStatusResponse(BaseModel):
    job_id: uuid.UUID
    status: str


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=RefreshAcceptedResponse)
async def trigger_refresh(
    background_tasks: BackgroundTasks,
    x_refresh_key: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> RefreshAcceptedResponse:
    if not hmac.compare_digest(x_refresh_key or "", settings.refresh_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh key")

    result = await session.execute(
        select(DigestCycle)
        .where(DigestCycle.status.in_(["pending", "running"]))
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return RefreshAcceptedResponse(job_id=existing.id, status=existing.status, created=False)

    now = datetime.now(timezone.utc)
    cycle = DigestCycle(
        status="pending",
        window_start=now - timedelta(hours=settings.refresh_interval_hours),
        window_end=now,
    )
    session.add(cycle)
    try:
        await session.commit()
    except IntegrityError:
        # Concurrent request won the race — find and return the active cycle
        await session.rollback()
        logger.warning("Concurrent refresh detected via IntegrityError; returning existing cycle")
        result = await session.execute(
            select(DigestCycle)
            .where(DigestCycle.status.in_(["pending", "running"]))
            .limit(1)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return RefreshAcceptedResponse(job_id=existing.id, status=existing.status, created=False)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Concurrent refresh in progress")

    await session.refresh(cycle)

    background_tasks.add_task(run_pipeline, cycle.id, AsyncSessionLocal)

    return RefreshAcceptedResponse(job_id=cycle.id, status="pending", created=True)


@router.get("/{job_id}", response_model=RefreshStatusResponse)
async def get_refresh_status(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> RefreshStatusResponse:
    cycle = await session.get(DigestCycle, job_id)
    if cycle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return RefreshStatusResponse(job_id=cycle.id, status=cycle.status)
