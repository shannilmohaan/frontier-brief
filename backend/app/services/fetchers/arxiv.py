import asyncio
import logging
from datetime import datetime, timedelta, timezone

import feedparser
import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_QUERY = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL"
MAX_RESULTS = 100


class ArxivFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 48) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    ARXIV_API_URL,
                    params={
                        "search_query": ARXIV_QUERY,
                        "start": 0,
                        "max_results": MAX_RESULTS,
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                    },
                )
                resp.raise_for_status()
                content = resp.text
        except Exception as exc:
            logger.error("arXiv fetch failed: %s", exc)
            return []

        try:
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, content)
        except Exception as exc:
            logger.error("arXiv parse failed: %s", exc)
            return []

        items: list[FetchedItem] = []
        for entry in feed.entries:
            try:
                published_struct = entry.get("published_parsed")
                if not published_struct:
                    continue
                published_at = datetime(*published_struct[:6], tzinfo=timezone.utc)
                if published_at < cutoff:
                    continue

                title = entry.get("title", "").replace("\n", " ").strip()
                summary = entry.get("summary", "").replace("\n", " ").strip()[:600]
                link = entry.get("link", "")
                if not link:
                    continue

                # Prefer the abs URL over the PDF link
                arxiv_id = entry.get("id", link)

                items.append(
                    FetchedItem(
                        title=title,
                        summary=summary,
                        source_name="arXiv",
                        source_url=arxiv_id,
                        domain_tags=classify_domains(f"{title} {summary}"),
                        published_at=published_at,
                        content_type="paper",
                    )
                )
            except Exception as exc:
                logger.warning("Skipping arXiv entry due to parse error: %s", exc)
                continue

        return items
