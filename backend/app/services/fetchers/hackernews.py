import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"
_AI_QUERY = "AI LLM GPT Claude machine learning neural network agent model"
_MIN_POINTS = 10


class HackerNewsFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        cutoff_unix = int(cutoff.timestamp())

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    _ALGOLIA_URL,
                    params={
                        "query": _AI_QUERY,
                        "tags": "story",
                        "numericFilters": f"created_at_i>{cutoff_unix},points>{_MIN_POINTS}",
                        "hitsPerPage": 50,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.error("HN fetch failed: %s", exc)
            return []

        items: list[FetchedItem] = []
        for hit in data.get("hits", []):
            try:
                title = (hit.get("title") or "").strip()
                if not title:
                    continue

                # Only include items Claude's domain classifier recognises as AI-related
                tags = classify_domains(title)
                if not tags:
                    continue

                created_at = hit.get("created_at")
                if not created_at:
                    continue
                published_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if published_at < cutoff:
                    continue

                points = hit.get("points") or 0
                num_comments = hit.get("num_comments") or 0
                story_text = (hit.get("story_text") or "").strip()
                summary = story_text[:600] if story_text else (
                    f"Hacker News — {points} points, {num_comments} comments"
                )

                object_id = hit.get("objectID", "")
                if not object_id:
                    continue

                items.append(
                    FetchedItem(
                        title=title,
                        summary=summary,
                        source_name="Hacker News",
                        source_url=f"https://news.ycombinator.com/item?id={object_id}",
                        domain_tags=tags,
                        published_at=published_at,
                        content_type="discussion",
                    )
                )
            except Exception as exc:
                logger.warning("Skipping HN hit: %s", exc)
                continue

        logger.info("HN: %d AI items in last %dh window", len(items), self._window_hours)
        return items
