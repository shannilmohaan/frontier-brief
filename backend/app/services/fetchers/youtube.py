import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings
from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
_AI_QUERY = "artificial intelligence AI LLM machine learning agent deep learning"


class YouTubeFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours
        self._api_key = settings.youtube_api_key

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        published_after = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(
                    f"{YOUTUBE_API_BASE}/search",
                    params={
                        "part": "snippet",
                        "type": "video",
                        "q": _AI_QUERY,
                        "publishedAfter": published_after,
                        "maxResults": 25,
                        "order": "relevance",
                        "relevanceLanguage": "en",
                        "key": self._api_key,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                logger.error("YouTube search failed: %s", exc)
                return []

        items: list[FetchedItem] = []
        for hit in data.get("items", []):
            try:
                snippet = hit.get("snippet", {})
                title = (snippet.get("title") or "").strip()
                if not title:
                    continue

                video_id = hit.get("id", {}).get("videoId", "")
                if not video_id:
                    continue

                published_str = snippet.get("publishedAt", "")
                if not published_str:
                    continue
                published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                if published_at < cutoff:
                    continue

                description = (snippet.get("description") or "")[:600]
                channel_title = snippet.get("channelTitle", "YouTube")

                thumbnails = snippet.get("thumbnails", {})
                thumbnail_url: str | None = (
                    thumbnails.get("high", {}).get("url")
                    or thumbnails.get("medium", {}).get("url")
                    or thumbnails.get("default", {}).get("url")
                )

                items.append(
                    FetchedItem(
                        title=title,
                        summary=description,
                        source_name=channel_title,
                        source_url=f"https://www.youtube.com/watch?v={video_id}",
                        domain_tags=classify_domains(f"{title} {description}"),
                        published_at=published_at,
                        content_type="video",
                        social_score=0.3,
                        thumbnail_url=thumbnail_url,
                    )
                )
            except Exception as exc:
                logger.warning("Skipping YouTube hit: %s", exc)

        logger.info("YouTube: %d AI videos in last %dh", len(items), self._window_hours)
        return items
