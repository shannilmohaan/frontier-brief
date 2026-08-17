import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings
from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Curated channel list — only known, high-quality AI creators (English).
# Format: (youtube_handle_without_@, display_name)
# Uses the uploads-playlist approach (2 API units per channel, vs 100 for search).
YOUTUBE_CHANNELS: list[tuple[str, str]] = [
    # Official AI labs
    ("OpenAI",           "OpenAI"),
    ("Anthropic",        "Anthropic"),
    # Top independent educators for builders
    ("AndrejKarpathy",   "Andrej Karpathy"),
    ("DeepLearningAI",   "DeepLearning.AI"),
    ("Fireship",         "Fireship"),
    # Framework / ecosystem channels
    ("LangChain",        "LangChain"),
    # Builder-focused AI creators
    ("ColeMedin",        "Cole Medin"),
    ("AIJasonZ",         "AI Jason"),
    ("daveebbelaar",     "Dave Ebbelaar"),
    ("mattpocockuk",     "Matt Pocock"),
    # Simon Willison YouTube (practical LLM/agent demos)
    ("simonw",           "Simon Willison"),
]


class YouTubeFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours
        self._api_key = settings.youtube_api_key

    async def fetch(self) -> list[FetchedItem]:
        if not self._api_key:
            logger.warning("YOUTUBE_API_KEY not set — skipping YouTube fetch")
            return []

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)

        async with httpx.AsyncClient(timeout=30.0) as client:
            resolve_results = await asyncio.gather(
                *[self._resolve_uploads_playlist(client, handle) for handle, _ in YOUTUBE_CHANNELS],
                return_exceptions=True,
            )

        resolved: list[tuple[str, str, str]] = []  # (handle, display_name, uploads_playlist_id)
        for (handle, display_name), result in zip(YOUTUBE_CHANNELS, resolve_results):
            if isinstance(result, Exception):
                logger.warning("Could not resolve channel @%s: %s", handle, result)
            elif result is None:
                logger.warning("Channel @%s not found on YouTube — skipping", handle)
            else:
                resolved.append((handle, display_name, result))

        async with httpx.AsyncClient(timeout=30.0) as client:
            video_results = await asyncio.gather(
                *[self._fetch_playlist_videos(client, display_name, playlist_id, cutoff)
                  for _, display_name, playlist_id in resolved],
                return_exceptions=True,
            )

        items: list[FetchedItem] = []
        for (_, display_name, _), result in zip(resolved, video_results):
            if isinstance(result, Exception):
                logger.error("YouTube playlist fetch failed for %s: %s", display_name, result)
            else:
                items.extend(result)

        logger.info("YouTube: %d videos from %d curated channels (last %dh)",
                    len(items), len(resolved), self._window_hours)
        return items

    async def _resolve_uploads_playlist(self, client: httpx.AsyncClient, handle: str) -> str | None:
        try:
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/channels",
                params={
                    "part": "contentDetails",
                    "forHandle": handle,
                    "key": self._api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            if not items:
                return None
            return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except Exception as exc:
            raise RuntimeError(f"Handle resolution failed: {exc}") from exc

    async def _fetch_playlist_videos(
        self,
        client: httpx.AsyncClient,
        display_name: str,
        playlist_id: str,
        cutoff: datetime,
    ) -> list[FetchedItem]:
        try:
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": playlist_id,
                    "maxResults": 10,
                    "key": self._api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("playlistItems failed for %s: %s", display_name, exc)
            return []

        items: list[FetchedItem] = []
        for hit in data.get("items", []):
            try:
                snippet = hit.get("snippet", {})

                # playlistItems returns removed/private videos with "Private video" title
                title = (snippet.get("title") or "").strip()
                if not title or title in ("Private video", "Deleted video"):
                    continue

                published_str = snippet.get("publishedAt", "")
                if not published_str:
                    continue
                published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                if published_at < cutoff:
                    continue

                resource = snippet.get("resourceId", {})
                video_id = resource.get("videoId", "")
                if not video_id:
                    continue

                description = (snippet.get("description") or "")[:600]

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
                        source_name=display_name,
                        source_url=f"https://www.youtube.com/watch?v={video_id}",
                        domain_tags=classify_domains(f"{title} {description}"),
                        published_at=published_at,
                        content_type="video",
                        social_score=0.3,
                        thumbnail_url=thumbnail_url,
                    )
                )
            except Exception as exc:
                logger.warning("Skipping %s video entry: %s", display_name, exc)

        logger.info("%s: %d videos in last %dh window", display_name, len(items),
                    int((datetime.now(timezone.utc) - cutoff).total_seconds() / 3600))
        return items
