import asyncio
import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

_TAVILY_URL = "https://api.tavily.com/search"

# (query, social_score) — X/LinkedIn queries score higher as content came from social platforms
_QUERIES: list[tuple[str, float]] = [
    ("artificial intelligence news this week", 0.4),
    ("large language model LLM breakthrough", 0.4),
    ("AI tools productivity startup", 0.4),
    ("AI machine learning site:x.com", 0.8),
    ("artificial intelligence site:linkedin.com", 0.8),
]


class WebArticlesFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        if not settings.tavily_api_key:
            logger.warning("TAVILY_API_KEY not set — skipping web article search")
            return []
        headers = {
            "Authorization": f"Bearer {settings.tavily_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            results = await asyncio.gather(
                *[self._search(client, headers, query, score) for query, score in _QUERIES],
                return_exceptions=True,
            )

        items: list[FetchedItem] = []
        for (query, _), result in zip(_QUERIES, results):
            if isinstance(result, Exception):
                logger.error("Tavily search failed for %r: %s", query, result)
            else:
                items.extend(result)

        seen: set[str] = set()
        unique: list[FetchedItem] = []
        for item in items:
            if item.source_url not in seen:
                seen.add(item.source_url)
                unique.append(item)

        logger.info("WebArticles: %d items after dedup", len(unique))
        return unique

    async def _search(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str],
        query: str,
        social_score: float,
    ) -> list[FetchedItem]:
        resp = await client.post(
            _TAVILY_URL,
            headers=headers,
            json={"query": query, "search_depth": "basic", "max_results": 10, "days": 7},
        )
        resp.raise_for_status()
        data = resp.json()

        items: list[FetchedItem] = []
        for r in data.get("results", []):
            title = (r.get("title") or "").strip()
            if not title:
                continue
            url = (r.get("url") or "").strip()
            if not url:
                continue

            content = (r.get("content") or "")[:600]
            domain_tags = classify_domains(f"{title} {content}")

            try:
                source_name = urlparse(url).netloc.replace("www.", "")
            except Exception:
                source_name = "Web"

            published_at: datetime = datetime.now(timezone.utc) - timedelta(hours=24)
            if r.get("published_date"):
                try:
                    published_at = datetime.fromisoformat(
                        r["published_date"].replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            images = r.get("images") or []
            thumbnail_url: str | None = images[0] if images else None

            items.append(
                FetchedItem(
                    title=title,
                    summary=content,
                    source_name=source_name,
                    source_url=url,
                    domain_tags=domain_tags,
                    published_at=published_at,
                    content_type="article",
                    social_score=social_score,
                    thumbnail_url=thumbnail_url,
                )
            )
        return items
