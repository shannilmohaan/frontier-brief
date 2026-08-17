import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

_SUBREDDITS = ["MachineLearning", "LocalLLaMA", "artificial"]
_MIN_SCORE = 50
_USER_AGENT = "FrontierBrief/1.0 (personal AI digest aggregator)"


class RedditFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)

        async with httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": _USER_AGENT},
            follow_redirects=True,
        ) as client:
            results = await asyncio.gather(
                *[self._fetch_subreddit(client, sub, cutoff) for sub in _SUBREDDITS],
                return_exceptions=True,
            )

        items: list[FetchedItem] = []
        for sub, result in zip(_SUBREDDITS, results):
            if isinstance(result, Exception):
                logger.error("Reddit fetch failed for r/%s: %s", sub, result)
            else:
                items.extend(result)

        logger.info("Reddit: %d items in last %dh window", len(items), self._window_hours)
        return items

    async def _fetch_subreddit(
        self, client: httpx.AsyncClient, subreddit: str, cutoff: datetime
    ) -> list[FetchedItem]:
        resp = await client.get(
            f"https://www.reddit.com/r/{subreddit}/top.json",
            params={"t": "week", "limit": 25, "raw_json": "1"},
        )
        resp.raise_for_status()
        data = resp.json()

        items: list[FetchedItem] = []
        for post in data.get("data", {}).get("children", []):
            try:
                p = post.get("data", {})
                score = p.get("score", 0)
                if score < _MIN_SCORE:
                    continue

                created_utc = p.get("created_utc")
                if not created_utc:
                    continue
                published_at = datetime.fromtimestamp(float(created_utc), tz=timezone.utc)
                if published_at < cutoff:
                    continue

                title = (p.get("title") or "").strip()
                if not title:
                    continue

                selftext = (p.get("selftext") or "").strip()
                # Skip removed/deleted posts
                if selftext in ("[removed]", "[deleted]"):
                    selftext = ""

                summary = selftext[:600] if selftext else (
                    f"r/{subreddit} — {score} upvotes, {p.get('num_comments', 0)} comments"
                )

                permalink = p.get("permalink", "")
                if not permalink:
                    continue

                domain_tags = classify_domains(f"{title} {summary}")

                items.append(
                    FetchedItem(
                        title=title,
                        summary=summary,
                        source_name=f"r/{subreddit}",
                        source_url=f"https://reddit.com{permalink}",
                        domain_tags=domain_tags,
                        published_at=published_at,
                        content_type="discussion",
                    )
                )
            except Exception as exc:
                logger.warning("Skipping Reddit post in r/%s: %s", subreddit, exc)
                continue

        return items
