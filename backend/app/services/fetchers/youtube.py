import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings
from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# YouTube handles for monitored channels
CHANNEL_HANDLES = [
    "andrejkarpathy",
    "YannicKilcher",
    "TwoMinutePapers",
    "aiexplained-official",
    "matthew_berman",
]


class YouTubeFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 48) -> None:
        self._window_hours = window_hours
        self._api_key = settings.youtube_api_key

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)
        items: list[FetchedItem] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            results = await asyncio.gather(
                *[self._fetch_channel(client, handle, cutoff) for handle in CHANNEL_HANDLES],
                return_exceptions=True,
            )

        for handle, result in zip(CHANNEL_HANDLES, results):
            if isinstance(result, Exception):
                logger.error("YouTube fetch failed for @%s: %s", handle, result)
            else:
                items.extend(result)

        return items

    async def _fetch_channel(
        self, client: httpx.AsyncClient, handle: str, cutoff: datetime
    ) -> list[FetchedItem]:
        channel_resp = await client.get(
            f"{YOUTUBE_API_BASE}/channels",
            params={
                "part": "contentDetails,snippet",
                "forHandle": handle,
                "key": self._api_key,
            },
        )
        channel_resp.raise_for_status()
        channel_data = channel_resp.json()

        if not channel_data.get("items"):
            logger.warning("No YouTube channel found for handle: %s", handle)
            return []

        channel_item = channel_data["items"][0]
        uploads_playlist = channel_item["contentDetails"]["relatedPlaylists"]["uploads"]
        channel_title = channel_item["snippet"]["title"]

        playlist_resp = await client.get(
            f"{YOUTUBE_API_BASE}/playlistItems",
            params={
                "part": "snippet",
                "playlistId": uploads_playlist,
                "maxResults": 15,
                "key": self._api_key,
            },
        )
        playlist_resp.raise_for_status()
        playlist_data = playlist_resp.json()

        items: list[FetchedItem] = []
        for video in playlist_data.get("items", []):
            snippet = video["snippet"]
            published_str = snippet.get("publishedAt", "")
            if not published_str:
                continue
            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            if published_at < cutoff:
                continue

            video_id = snippet.get("resourceId", {}).get("videoId", "")
            if not video_id:
                continue

            title = snippet.get("title") or ""
            if not title:
                continue  # private/deleted video — no usable content
            description = (snippet.get("description") or "")[:600]
            items.append(
                FetchedItem(
                    title=title,
                    summary=description,
                    source_name=channel_title,
                    source_url=f"https://www.youtube.com/watch?v={video_id}",
                    domain_tags=classify_domains(f"{title} {description}"),
                    published_at=published_at,
                    content_type="video",
                )
            )

        return items
