import hmac
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_session

router = APIRouter(prefix="/api/refresh", tags=["refresh"])


class RefreshAcceptedResponse(BaseModel):
    job_id: uuid.UUID
    status: str


class RefreshStatusResponse(BaseModel):
    job_id: uuid.UUID
    status: str


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=RefreshAcceptedResponse)
async def trigger_refresh(
    x_refresh_key: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> RefreshAcceptedResponse:
    if not hmac.compare_digest(x_refresh_key or "", settings.refresh_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh key")
    # Placeholder — full pipeline wiring in Phase 1d
    return RefreshAcceptedResponse(job_id=uuid.uuid4(), status="accepted")


@router.get("/{job_id}", response_model=RefreshStatusResponse)
async def get_refresh_status(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> RefreshStatusResponse:
    # Placeholder — full implementation in Phase 1d
    return RefreshStatusResponse(job_id=job_id, status="unknown")
