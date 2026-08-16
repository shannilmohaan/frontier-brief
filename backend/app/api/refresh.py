import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_session

router = APIRouter(prefix="/api/refresh", tags=["refresh"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def trigger_refresh(
    x_refresh_key: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if x_refresh_key != settings.refresh_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh key")
    # Placeholder — full pipeline wiring in Phase 1d
    job_id = str(uuid.uuid4())
    return {"job_id": job_id, "status": "accepted"}


@router.get("/{job_id}")
async def get_refresh_status(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    # Placeholder — full implementation in Phase 1d
    return {"job_id": job_id, "status": "unknown"}
