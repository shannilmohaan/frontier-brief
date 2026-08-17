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

PODCAST_FEEDS: list[tuple[str, str]] = [
    # Verified working RSS feeds — do not add guessed URLs here
    ("https://lexfridman.com/feed/podcast/",    "Lex Fridman Podcast"),
    ("https://twimlai.com/feed/",               "TWIML AI Podcast"),
    ("https://www.latent.space/feed",           "Latent Space"),
    ("https://practicalai.fm/rss",              "Practical AI"),
]
_HTML_TAG = re.compile(r"<[^>]+>")


class PodcastRssFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            results = await asyncio.gather(
                *[self._fetch_feed(client, url, name, cutoff) for url, name in PODCAST_FEEDS],
                return_exceptions=True,
            )

        items: list[FetchedItem] = []
        for (_, name), result in zip(PODCAST_FEEDS, results):
            if isinstance(result, Exception):
                logger.error("Podcast RSS failed for %s: %s", name, result)
            else:
                items.extend(result)

        logger.info("Podcasts: %d items", len(items))
        return items

    async def _fetch_feed(
        self,
        client: httpx.AsyncClient,
        url: str,
        source_name: str,
        cutoff: datetime,
    ) -> list[FetchedItem]:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("%s RSS unavailable: %s", source_name, exc)
            return []

        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, resp.text)

        items: list[FetchedItem] = []
        for entry in feed.entries:
            try:
                published_at: datetime | None = None
                if entry.get("published_parsed"):
                    published_at = datetime(*entry["published_parsed"][:6], tzinfo=timezone.utc)
                elif entry.get("published"):
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

                raw_summary = (
                    entry.get("summary")
                    or (
                        entry.get("content", [{}])[0].get("value", "")
                        if entry.get("content")
                        else ""
                    )
                    or ""
                )
                summary = _HTML_TAG.sub(" ", raw_summary)[:600]
                domain_tags = classify_domains(f"{title} {summary}")

                # Episode artwork from itunes:image or image tag
                thumbnail_url: str | None = None
                img = entry.get("image")
                if img:
                    thumbnail_url = getattr(img, "href", None) or (
                        img.get("href") if isinstance(img, dict) else None
                    )
                if not thumbnail_url:
                    itunes_img = entry.get("itunes_image") or {}
                    if isinstance(itunes_img, dict):
                        thumbnail_url = itunes_img.get("href")

                items.append(
                    FetchedItem(
                        title=title,
                        summary=summary,
                        source_name=source_name,
                        source_url=link,
                        domain_tags=domain_tags,
                        published_at=published_at,
                        content_type="podcast",
                        social_score=0.2,
                        thumbnail_url=thumbnail_url,
                    )
                )
            except Exception as exc:
                logger.warning("Skipping %s entry: %s", source_name, exc)

        logger.info("%s: %d items", source_name, len(items))
        return items
