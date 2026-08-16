from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.fetchers.arxiv import ArxivFetcher
from app.services.fetchers.base import FetchedItem

REQUIRED_FIELDS = {"title", "summary", "source_name", "source_url", "domain_tags", "published_at", "content_type"}

NOW = datetime.now(timezone.utc)
RECENT_DATE = (NOW - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
OLD_DATE = (NOW - timedelta(hours=72)).strftime("%Y-%m-%dT%H:%M:%SZ")

ARXIV_ATOM_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <title>Agentic Reasoning with Large Language Models</title>
    <summary>We propose a new framework for autonomous agents using LLMs.</summary>
    <published>{published}</published>
    <link href="http://arxiv.org/abs/2401.00001v1" rel="alternate" type="text/html"/>
  </entry>
</feed>"""

EMPTY_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"></feed>"""


@pytest.mark.asyncio
async def test_arxiv_fetcher_returns_recent_papers() -> None:
    atom_content = ARXIV_ATOM_TEMPLATE.format(published=RECENT_DATE)
    fetcher = ArxivFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.text = atom_content
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.arxiv.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert len(items) == 1
    item = items[0]
    assert isinstance(item, FetchedItem)
    assert all(hasattr(item, f) for f in REQUIRED_FIELDS)
    assert item.source_name == "arXiv"
    assert item.content_type == "paper"
    assert "arxiv.org" in item.source_url
    assert item.title != ""
    assert item.summary != ""


@pytest.mark.asyncio
async def test_arxiv_fetcher_skips_old_papers() -> None:
    atom_content = ARXIV_ATOM_TEMPLATE.format(published=OLD_DATE)
    fetcher = ArxivFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.text = atom_content
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.arxiv.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []


@pytest.mark.asyncio
async def test_arxiv_fetcher_returns_empty_on_no_results() -> None:
    fetcher = ArxivFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.text = EMPTY_ATOM
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.arxiv.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []


@pytest.mark.asyncio
async def test_arxiv_fetcher_returns_empty_on_http_error() -> None:
    fetcher = ArxivFetcher(window_hours=48)

    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Connection timeout")

    with patch("app.services.fetchers.arxiv.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []
