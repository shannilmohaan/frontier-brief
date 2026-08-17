import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.db.database import get_session
from app.db.models import DigestCycle, DigestItem, SourceItem

router = APIRouter(prefix="/api/digest", tags=["digest"])

_MAX_RESPONSE_ITEMS = 100


class DigestItemSchema(BaseModel):
    id: uuid.UUID
    source_title: str
    narrative: str
    why_it_matters: str | None = None
    what_changed: str | None = None
    who_should_care: str | None = None
    build_impact: str | None = None
    production_readiness: str | None = None
    should_i_use: str | None = None
    importance: int = 3
    source_name: str
    source_url: str
    content_type: str
    domain_tags: list[str]
    relevance_score: float
    created_at: datetime
    thumbnail_url: str | None = None


class LatestDigestResponse(BaseModel):
    items: list[DigestItemSchema]
    domain_filter: str | None
    cycle_id: uuid.UUID | None


class CycleInfo(BaseModel):
    id: uuid.UUID
    completed_at: datetime
    items_synthesized: int


class HistoryResponse(BaseModel):
    cycles: list[CycleInfo]


@router.get("/history", response_model=HistoryResponse)
async def get_digest_history(
    limit: int = Query(default=20, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
) -> HistoryResponse:
    result = await session.execute(
        select(DigestCycle)
        .where(DigestCycle.status == "completed")
        .order_by(DigestCycle.completed_at.desc())
        .limit(limit)
    )
    cycles = result.scalars().all()
    return HistoryResponse(
        cycles=[
            CycleInfo(
                id=c.id,
                completed_at=c.completed_at,
                items_synthesized=c.items_synthesized,
            )
            for c in cycles
        ]
    )


@router.get("/latest", response_model=LatestDigestResponse)
async def get_latest_digest(
    domain: str | None = Query(default=None, description="Filter by domain name", max_length=100),
    cycle_id: uuid.UUID | None = Query(default=None, description="Load a specific past cycle"),
    session: AsyncSession = Depends(get_session),
) -> LatestDigestResponse:
    if cycle_id:
        cycle_result = await session.execute(
            select(DigestCycle)
            .where(DigestCycle.id == cycle_id, DigestCycle.status == "completed")
        )
    else:
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
        .options(joinedload(DigestItem.source_item))
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
                source_title=row.source_item.title if row.source_item else "",
                narrative=row.narrative,
                why_it_matters=row.why_it_matters,
                what_changed=row.what_changed,
                who_should_care=row.who_should_care,
                build_impact=row.build_impact,
                production_readiness=row.production_readiness,
                should_i_use=row.should_i_use,
                importance=row.importance,
                source_name=row.source_name,
                source_url=row.source_url,
                content_type=row.content_type,
                domain_tags=row.domain_tags,
                relevance_score=row.relevance_score,
                created_at=row.created_at,
                thumbnail_url=row.source_item.thumbnail_url if row.source_item else None,
            )
            for row in rows
        ],
        domain_filter=domain,
        cycle_id=cycle.id,
    )


@router.delete("/clear-all", status_code=204)
async def clear_all_digest_data(
    token: str = Query(..., description="Admin token from ADMIN_TOKEN env var"),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Wipe all digest cycles, source items, and digest items. Requires ADMIN_TOKEN env var."""
    expected = os.getenv("ADMIN_TOKEN", "")
    if not expected or token != expected:
        raise HTTPException(status_code=403, detail="Forbidden")
    await session.execute(sa_delete(DigestItem))
    await session.execute(sa_delete(SourceItem))
    await session.execute(sa_delete(DigestCycle))
    await session.commit()
