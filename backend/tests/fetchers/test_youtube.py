from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.services.fetchers.base import FetchedItem
from app.services.fetchers.youtube import YouTubeFetcher

REQUIRED_FIELDS = {"title", "summary", "source_name", "source_url", "domain_tags", "published_at", "content_type"}

NOW = datetime.now(timezone.utc)


def _make_item(suffix: str = "") -> FetchedItem:
    return FetchedItem(
        title=f"Agentic AI Breakthrough{suffix}",
        summary="A video about autonomous agent systems.",
        source_name="Test Channel",
        source_url=f"https://www.youtube.com/watch?v=vid{suffix}",
        domain_tags=["Agentic AI"],
        published_at=NOW - timedelta(hours=12),
        content_type="video",
    )


@pytest.mark.asyncio
async def test_youtube_fetcher_returns_items_from_all_channels() -> None:
    fetcher = YouTubeFetcher(window_hours=48)

    with patch.object(fetcher, "_fetch_channel", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [_make_item()]
        items = await fetcher.fetch()

    assert len(items) == 5  # one per channel
    item = items[0]
    assert isinstance(item, FetchedItem)
    assert all(hasattr(item, f) for f in REQUIRED_FIELDS)
    assert item.source_url.startswith("https://www.youtube.com/watch?v=")
    assert item.content_type == "video"
    assert item.title != ""
    assert item.source_name != ""


@pytest.mark.asyncio
async def test_youtube_fetcher_returns_empty_when_channel_returns_none() -> None:
    fetcher = YouTubeFetcher(window_hours=48)

    with patch.object(fetcher, "_fetch_channel", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []
        items = await fetcher.fetch()

    assert items == []


@pytest.mark.asyncio
async def test_youtube_fetcher_continues_when_one_channel_raises() -> None:
    fetcher = YouTubeFetcher(window_hours=48)
    call_count = 0

    async def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Simulated channel fetch error")
        return [_make_item(str(call_count))]

    with patch.object(fetcher, "_fetch_channel", side_effect=side_effect):
        items = await fetcher.fetch()

    # 4 of 5 channels succeeded
    assert len(items) == 4


@pytest.mark.asyncio
async def test_youtube_fetcher_all_fields_present() -> None:
    fetcher = YouTubeFetcher(window_hours=48)

    with patch.object(fetcher, "_fetch_channel", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [_make_item()]
        items = await fetcher.fetch()

    assert items
    item = items[0]
    for field in REQUIRED_FIELDS:
        value = getattr(item, field)
        assert value is not None, f"Field '{field}' is None"
        if isinstance(value, str):
            assert value != "", f"Field '{field}' is empty string"
