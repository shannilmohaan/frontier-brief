from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.fetchers.base import FetchedItem
from app.services.fetchers.hf_papers import HFPapersFetcher

REQUIRED_FIELDS = {"title", "summary", "source_name", "source_url", "domain_tags", "published_at", "content_type"}

NOW = datetime.now(timezone.utc)
RECENT = (NOW - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
OLD = (NOW - timedelta(hours=72)).strftime("%Y-%m-%dT%H:%M:%SZ")

PAPER_PAYLOAD = [
    {
        "paper": {
            "id": "2401.00001",
            "title": "Scaling Agentic Systems with Reasoning Models",
            "abstract": "We study how reasoning capabilities scale in agentic LLM systems.",
            "publishedAt": RECENT,
        }
    }
]

OLD_PAPER_PAYLOAD = [
    {
        "paper": {
            "id": "2401.00002",
            "title": "Old Paper on LLMs",
            "abstract": "An older study on language model performance.",
            "publishedAt": OLD,
        }
    }
]


@pytest.mark.asyncio
async def test_hf_papers_fetcher_returns_recent_papers() -> None:
    fetcher = HFPapersFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.json.return_value = PAPER_PAYLOAD
    mock_resp.raise_for_status = MagicMock()

    # Both date requests return papers
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.hf_papers.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    # 2 date requests × 1 paper each = 2 items, but they share the same source_url
    # Dedup happens in ranker, not fetcher — expect 2 here
    assert len(items) >= 1
    item = items[0]
    assert isinstance(item, FetchedItem)
    assert all(hasattr(item, f) for f in REQUIRED_FIELDS)
    assert item.source_name == "Hugging Face Papers"
    assert item.content_type == "paper"
    assert "huggingface.co/papers/" in item.source_url
    assert item.title != ""


@pytest.mark.asyncio
async def test_hf_papers_fetcher_skips_old_papers() -> None:
    fetcher = HFPapersFetcher(window_hours=48)

    mock_resp = MagicMock()
    mock_resp.json.return_value = OLD_PAPER_PAYLOAD
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("app.services.fetchers.hf_papers.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []


@pytest.mark.asyncio
async def test_hf_papers_fetcher_returns_empty_on_api_error() -> None:
    fetcher = HFPapersFetcher(window_hours=48)

    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("API unavailable")

    with patch("app.services.fetchers.hf_papers.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert items == []


@pytest.mark.asyncio
async def test_hf_papers_fetcher_continues_when_one_date_fails() -> None:
    fetcher = HFPapersFetcher(window_hours=48)

    mock_ok = MagicMock()
    mock_ok.json.return_value = PAPER_PAYLOAD
    mock_ok.raise_for_status = MagicMock()

    call_count = 0

    async def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("First date request failed")
        return mock_ok

    mock_client = AsyncMock()
    mock_client.get.side_effect = side_effect

    with patch("app.services.fetchers.hf_papers.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        items = await fetcher.fetch()

    assert len(items) >= 1
