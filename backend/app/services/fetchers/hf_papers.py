import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

HF_PAPERS_API = "https://huggingface.co/api/daily_papers"


class HFPapersFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 48) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        items: list[FetchedItem] = []

        # Fetch today and yesterday to cover the full 48h window
        dates_to_fetch = [
            datetime.now(timezone.utc).date(),
            (datetime.now(timezone.utc) - timedelta(days=1)).date(),
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for date in dates_to_fetch:
                try:
                    resp = await client.get(HF_PAPERS_API, params={"date": date.isoformat()})
                    resp.raise_for_status()
                    papers = resp.json()
                    items.extend(_parse_papers(papers, cutoff))
                except Exception as exc:
                    logger.error("HF Papers fetch failed for %s: %s", date, exc)

        return items


def _parse_papers(papers: list[dict], cutoff: datetime) -> list[FetchedItem]:
    items: list[FetchedItem] = []
    for paper in papers:
        try:
            # HF API structure: paper["paper"] contains the metadata
            paper_data = paper.get("paper", paper)
            published_str = paper_data.get("publishedAt") or paper.get("publishedAt", "")
            if not published_str:
                continue

            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            if published_at < cutoff:
                continue

            title = paper_data.get("title", "").strip()
            abstract = paper_data.get("abstract", "").strip()[:600]
            arxiv_id = paper_data.get("id", "")
            if not arxiv_id or not title:
                continue

            source_url = f"https://huggingface.co/papers/{arxiv_id}"

            items.append(
                FetchedItem(
                    title=title,
                    summary=abstract,
                    source_name="Hugging Face Papers",
                    source_url=source_url,
                    domain_tags=classify_domains(f"{title} {abstract}"),
                    published_at=published_at,
                    content_type="paper",
                )
            )
        except Exception as exc:
            logger.warning("Skipping HF paper entry: %s", exc)
            continue

    return items
