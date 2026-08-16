import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session

router = APIRouter(prefix="/api/digest", tags=["digest"])


class DigestItemSchema(BaseModel):
    id: uuid.UUID
    narrative: str
    source_name: str
    source_url: str
    content_type: str
    domain_tags: list[str]
    relevance_score: float
    created_at: datetime


class LatestDigestResponse(BaseModel):
    items: list[DigestItemSchema]
    domain_filter: str | None
    cycle_id: uuid.UUID | None


@router.get("/latest", response_model=LatestDigestResponse)
async def get_latest_digest(
    domain: str | None = Query(default=None, description="Filter by domain name"),
    session: AsyncSession = Depends(get_session),
) -> LatestDigestResponse:
    # Placeholder — full implementation in Phase 1d
    return LatestDigestResponse(items=[], domain_filter=domain, cycle_id=None)
