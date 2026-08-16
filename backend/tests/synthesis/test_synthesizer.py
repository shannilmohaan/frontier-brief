import json
import re
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.services.fetchers.base import FetchedItem
from app.services.synthesis.synthesizer import SynthesizedItem, synthesize


def _item(
    url: str,
    domain: str = "Agentic AI",
    source_name: str = "Test Source",
    domain_tags: list[str] | None = None,
) -> FetchedItem:
    return FetchedItem(
        title="Test Title",
        summary="Test summary text.",
        source_name=source_name,
        source_url=url,
        domain_tags=domain_tags if domain_tags is not None else [domain],
        published_at=datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc),
        content_type="paper",
    )


def _claude_response(items: list[FetchedItem]) -> str:
    return json.dumps(
        [
            {
                "source_url": item.source_url,
                "narrative": f"This is a two-sentence narrative about {item.title}. It matters because it advances the state of the art.",
            }
            for item in items
        ]
    )


@pytest.mark.asyncio
async def test_synthesize_returns_synthesized_items():
    items = [_item("https://a.com"), _item("https://b.com")]
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = _claude_response(items)
        results = await synthesize(items)

    assert len(results) == 2
    assert all(isinstance(r, SynthesizedItem) for r in results)
    assert all(r.narrative for r in results)
    assert {r.source_url for r in results} == {"https://a.com", "https://b.com"}


@pytest.mark.asyncio
async def test_synthesize_appends_citation_deterministically():
    item = _item("https://arxiv.org/abs/1234", source_name="arXiv")
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = _claude_response([item])
        results = await synthesize([item])

    assert "Source: [arXiv](https://arxiv.org/abs/1234)" in results[0].narrative


@pytest.mark.asyncio
async def test_synthesize_preserves_source_metadata():
    item = _item("https://arxiv.org/abs/1234", domain="AI Research", source_name="arXiv")
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = _claude_response([item])
        results = await synthesize([item])

    assert results[0].source_name == "arXiv"
    assert results[0].source_url == "https://arxiv.org/abs/1234"
    assert results[0].content_type == "paper"
    assert results[0].domain_tags == ["AI Research"]
    assert results[0].published_at == datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_synthesize_caps_at_five_per_domain():
    items = [_item(f"https://example.com/{i}") for i in range(8)]
    captured: list[list] = []

    async def fake_complete(system: str, user: str) -> str:
        urls = re.findall(r'"source_url": "(https://[^"]+)"', user)
        batch = [_item(u) for u in urls]
        captured.append(batch)
        return _claude_response(batch)

    with patch("app.services.synthesis.synthesizer.claude_client.complete", side_effect=fake_complete):
        await synthesize(items)

    assert all(len(batch) <= 5 for batch in captured)


@pytest.mark.asyncio
async def test_synthesize_handles_malformed_json():
    items = [_item("https://a.com")]
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = "not valid json at all"
        results = await synthesize(items)

    assert results == []


@pytest.mark.asyncio
async def test_synthesize_handles_json_object_instead_of_array():
    items = [_item("https://a.com")]
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = '{"error": "unexpected"}'
        results = await synthesize(items)

    assert results == []


@pytest.mark.asyncio
async def test_synthesize_handles_json_wrapped_in_markdown():
    items = [_item("https://a.com")]
    wrapped = "```json\n" + _claude_response(items) + "\n```"
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = wrapped
        results = await synthesize(items)

    assert len(results) == 1


@pytest.mark.asyncio
async def test_synthesize_handles_json_with_preamble():
    items = [_item("https://a.com")]
    preamble = "Here is the requested JSON array:\n" + _claude_response(items)
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = preamble
        results = await synthesize(items)

    assert len(results) == 1


@pytest.mark.asyncio
async def test_synthesize_skips_failed_domain_continues_others():
    item_a = _item("https://a.com", domain="Agentic AI")
    item_b = _item("https://b.com", domain="AI Research")

    call_count = 0

    async def selective_fail(system: str, user: str) -> str:
        nonlocal call_count
        call_count += 1
        if "Agentic AI" in user:
            raise RuntimeError("API error")
        return _claude_response([item_b])

    with patch("app.services.synthesis.synthesizer.claude_client.complete", side_effect=selective_fail):
        results = await synthesize([item_a, item_b])

    assert call_count == 2
    assert len(results) == 1
    assert results[0].source_url == "https://b.com"


@pytest.mark.asyncio
async def test_synthesize_skips_unmatched_urls_in_response():
    item = _item("https://real.com")
    bad_response = json.dumps([{"source_url": "https://different.com", "narrative": "Some text."}])
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = bad_response
        results = await synthesize([item])

    assert results == []


@pytest.mark.asyncio
async def test_synthesize_skips_empty_narrative():
    item = _item("https://a.com")
    response = json.dumps([{"source_url": "https://a.com", "narrative": ""}])
    with patch("app.services.synthesis.synthesizer.claude_client.complete", new_callable=AsyncMock) as mock:
        mock.return_value = response
        results = await synthesize([item])

    assert results == []


@pytest.mark.asyncio
async def test_synthesize_empty_domain_tags_falls_back_to_ai_research():
    item = _item("https://a.com", domain_tags=[])
    captured_prompts: list[str] = []

    async def capture(system: str, user: str) -> str:
        captured_prompts.append(user)
        return _claude_response([item])

    with patch("app.services.synthesis.synthesizer.claude_client.complete", side_effect=capture):
        results = await synthesize([item])

    assert any("AI Research" in p for p in captured_prompts)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_synthesize_empty_input_returns_empty():
    results = await synthesize([])
    assert results == []
