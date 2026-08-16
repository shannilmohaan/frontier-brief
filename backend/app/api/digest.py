import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_session
from app.db.models import DigestCycle, DigestItem

router = APIRouter(prefix="/api/digest", tags=["digest"])

# Safety cap: max_items_per_domain × number of known domains (10)
_MAX_RESPONSE_ITEMS = 100


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
    domain: str | None = Query(default=None, description="Filter by domain name", max_length=100),
    session: AsyncSession = Depends(get_session),
) -> LatestDigestResponse:
    cycle_result = await session.execute(
        select(DigestCycle)
        .where(DigestCycle.status == "completed")
        .order_by(DigestCycle.completed_at.desc())
        .limit(1)
    )
    cycle = cycle_result.scalar_one_or_none()
    if cycle is None:
        return LatestDigestResponse(items=[], domain_filter=domain, cycle_id=None)

    query = (
        select(DigestItem)
        .where(DigestItem.cycle_id == cycle.id)
        .order_by(DigestItem.relevance_score.desc())
        .limit(settings.max_items_per_domain if domain else _MAX_RESPONSE_ITEMS)
    )
    if domain:
        query = query.where(DigestItem.domain_tags.contains([domain]))

    items_result = await session.execute(query)
    rows = items_result.scalars().all()

    return LatestDigestResponse(
        items=[
            DigestItemSchema(
                id=row.id,
                narrative=row.narrative,
                source_name=row.source_name,
                source_url=row.source_url,
                content_type=row.content_type,
                domain_tags=row.domain_tags,
                relevance_score=row.relevance_score,
                created_at=row.created_at,
            )
            for row in rows
        ],
        domain_filter=domain,
        cycle_id=cycle.id,
    )
