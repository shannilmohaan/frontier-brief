from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.fetchers.base import FetchedItem
from app.services.fetchers.the_batch import TheBatchFetcher

REQUIRED_FIELDS = {"title", "summary", "source_name", "source_url", "domain_tags", "published_at", "content_type"}

NOW = datetime.now(timezone.utc)
RECENT_RFC2822 = format_datetime(NOW - timedelta(hours=12))
OLD_RFC2822 = format_datetime(NOW - timedelta(hours=72))

RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>The Batch</title>
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{description}</description>
      <pubDate>{pub_date}</pubDate>
    </item>
  </channel>
</rss>"""

EMPTY_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>The Batch</title></channel></rss>"""


@pytest.mark.asyncio
async def test_the_batch_fetcher_returns_recent_items() -> None:
    rss = RSS_TEMPLATE.format(
        title="AI Agents Take Center Stage",
        link="https://www.deeplearning.ai/the-batch/issue-123/",
        description="This week in AI: autonomous agents are reshaping software engineering.",
        pub_date=RECENT_RFC2822,
    )
    fetcher = TheBatchFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.text = rss
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.the_batch.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert len(items) == 1
    item = items[0]
    assert isinstance(item, FetchedItem)
    assert all(hasattr(item, f) for f in REQUIRED_FIELDS)
    assert item.source_name == "The Batch"
    assert item.content_type == "newsletter"
    assert item.source_url.startswith("https://")


@pytest.mark.asyncio
async def test_the_batch_fetcher_returns_empty_when_outside_window() -> None:
    rss = RSS_TEMPLATE.format(
        title="Old Issue",
        link="https://www.deeplearning.ai/the-batch/issue-100/",
        description="Old content.",
        pub_date=OLD_RFC2822,
    )
    fetcher = TheBatchFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.text = rss
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.the_batch.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []


@pytest.mark.asyncio
async def test_the_batch_fetcher_handles_empty_feed_gracefully() -> None:
    fetcher = TheBatchFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.text = EMPTY_RSS
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.the_batch.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []


@pytest.mark.asyncio
async def test_the_batch_fetcher_returns_empty_on_http_error() -> None:
    fetcher = TheBatchFetcher(window_hours=48)

    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Connection refused")

    with patch("app.services.fetchers.the_batch.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []
