import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

_FEEDS = [
    "https://news.google.com/rss/search?q=artificial+intelligence&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=LLM+large+language+model&hl=en&gl=US&ceid=US:en",
]
_HTML_TAG = re.compile(r"<[^>]+>")


class GoogleNewsFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            results = await asyncio.gather(
                *[self._fetch_feed(client, url, cutoff) for url in _FEEDS],
                return_exceptions=True,
            )

        items: list[FetchedItem] = []
        seen: set[str] = set()
        for result in results:
            if isinstance(result, Exception):
                logger.error("Google News fetch failed: %s", result)
            else:
                for item in result:
                    if item.source_url not in seen:
                        seen.add(item.source_url)
                        items.append(item)

        logger.info("GoogleNews: %d items", len(items))
        return items

    async def _fetch_feed(
        self, client: httpx.AsyncClient, url: str, cutoff: datetime
    ) -> list[FetchedItem]:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("Google News RSS unavailable: %s", exc)
            return []

        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, resp.text)

        items: list[FetchedItem] = []
        for entry in feed.entries:
            try:
                published_at: datetime | None = None
                if entry.get("published"):
                    try:
                        published_at = parsedate_to_datetime(entry["published"])
                    except Exception:
                        pass
                if published_at is None or published_at < cutoff:
                    continue

                title = _HTML_TAG.sub(" ", entry.get("title", "")).strip()
                if not title:
                    continue

                link = entry.get("link", "")
                if not link:
                    continue

                summary = _HTML_TAG.sub(" ", entry.get("summary", ""))[:600]
                domain_tags = classify_domains(f"{title} {summary}")

                source_obj = entry.get("source")
                source_name = (
                    source_obj.get("title", "Google News")
                    if isinstance(source_obj, dict)
                    else "Google News"
                )

                items.append(
                    FetchedItem(
                        title=title,
                        summary=summary,
                        source_name=source_name,
                        source_url=link,
                        domain_tags=domain_tags,
                        published_at=published_at,
                        content_type="article",
                        social_score=0.6,
                    )
                )
            except Exception as exc:
                logger.warning("Skipping Google News entry: %s", exc)

        return items
