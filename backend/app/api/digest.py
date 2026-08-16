from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("/latest")
async def get_latest_digest(
    domain: str | None = Query(default=None, description="Filter by domain name"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    # Placeholder — full implementation in Phase 1d
    return {"items": [], "domain_filter": domain, "cycle_id": None}
