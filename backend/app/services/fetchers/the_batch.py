import asyncio
import logging
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

THE_BATCH_RSS_URL = "https://www.deeplearning.ai/the-batch/feed/rss/"


class TheBatchFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 48) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(THE_BATCH_RSS_URL)
                resp.raise_for_status()
                content = resp.text
        except Exception as exc:
            logger.error("The Batch fetch failed: %s", exc)
            return []

        try:
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, content)
        except Exception as exc:
            logger.error("The Batch parse failed: %s", exc)
            return []

        items: list[FetchedItem] = []
        for entry in feed.entries:
            try:
                published_at = _parse_date(entry)
                if published_at is None or published_at < cutoff:
                    continue

                title = entry.get("title", "").strip()
                # Prefer summary, fall back to content
                summary = (
                    entry.get("summary")
                    or _extract_content(entry)
                    or ""
                ).strip()[:600]
                link = entry.get("link", "")
                if not link:
                    continue

                items.append(
                    FetchedItem(
                        title=title,
                        summary=summary,
                        source_name="The Batch",
                        source_url=link,
                        domain_tags=classify_domains(f"{title} {summary}"),
                        published_at=published_at,
                        content_type="newsletter",
                    )
                )
            except Exception as exc:
                logger.warning("Skipping The Batch entry: %s", exc)
                continue

        if not items:
            logger.info("The Batch: no new items in the last %dh window (weekly cadence)", self._window_hours)

        return items


def _parse_date(entry: dict) -> datetime | None:  # type: ignore[type-arg]
    if entry.get("published_parsed"):
        try:
            return datetime(*entry["published_parsed"][:6], tzinfo=timezone.utc)
        except Exception:
            pass
    if entry.get("published"):
        try:
            return parsedate_to_datetime(entry["published"])
        except Exception:
            pass
    return None


def _extract_content(entry: dict) -> str:  # type: ignore[type-arg]
    content_list = entry.get("content", [])
    if content_list and isinstance(content_list, list):
        return content_list[0].get("value", "")
    return ""
