import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime

from app.services.fetchers.base import ContentType, FetchedItem
from app.services.synthesis import claude_client
from app.services.synthesis.prompts import SYSTEM_PROMPT, make_user_prompt

logger = logging.getLogger(__name__)

_MAX_ITEMS_PER_DOMAIN = 5


@dataclass
class SynthesizedItem:
    narrative: str
    source_name: str
    source_url: str
    content_type: ContentType
    domain_tags: list[str]
    published_at: datetime
    why_it_matters: str = ""
    importance: int = 3


def _group_by_domain(items: list[FetchedItem]) -> dict[str, list[FetchedItem]]:
    groups: dict[str, list[FetchedItem]] = {}
    for item in items:
        primary = item.domain_tags[0] if item.domain_tags else "AI Research"
        groups.setdefault(primary, []).append(item)
    return {domain: domain_items[:_MAX_ITEMS_PER_DOMAIN] for domain, domain_items in groups.items()}


def _extract_json(raw: str | None) -> str:
    """Extract the JSON array from Claude's response regardless of surrounding text or fences."""
    if not raw:
        return "[]"
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    return match.group(0) if match else raw


def _parse_response(raw: str, fetched_by_url: dict[str, FetchedItem]) -> list[SynthesizedItem]:
    try:
        parsed = json.loads(_extract_json(raw))
    except (json.JSONDecodeError, ValueError):
        logger.warning("Claude returned non-JSON; skipping domain batch")
        return []

    if not isinstance(parsed, list):
        logger.warning("Claude returned JSON but not an array; skipping domain batch")
        return []

    results: list[SynthesizedItem] = []
    for element in parsed:
        url = element.get("source_url", "").strip()
        narrative = element.get("narrative", "").strip()
        if not url or not narrative or url not in fetched_by_url:
            logger.warning(
                "Skipped item: url=%r has_narrative=%s url_in_dict=%s dict_sample=%r",
                url[:120] if url else url,
                bool(narrative),
                url in fetched_by_url,
                list(fetched_by_url.keys())[:2],
            )
            continue
        fetched = fetched_by_url[url]
        # Truncate before citation to limit prompt-injection blast radius
        narrative = narrative[:1000]
        why_it_matters = str(element.get("why_it_matters", "") or "")[:500].strip()
        try:
            importance = max(1, min(5, int(element.get("importance", 3))))
        except (TypeError, ValueError):
            importance = 3
        # Citation is appended deterministically — not left to Claude — to guarantee accuracy.
        cited_narrative = f"{narrative.rstrip()}\n\nSource: [{fetched.source_name}]({url})"
        results.append(
            SynthesizedItem(
                narrative=cited_narrative,
                source_name=fetched.source_name,
                source_url=url,
                content_type=fetched.content_type,
                domain_tags=fetched.domain_tags,
                published_at=fetched.published_at,
                why_it_matters=why_it_matters,
                importance=importance,
            )
        )
    return results


async def _synthesize_domain(domain: str, items: list[FetchedItem]) -> list[SynthesizedItem]:
    fetched_by_url = {item.source_url: item for item in items}
    logger.info(
        "Synthesizing domain '%s': %d items, avg_summary_len=%d",
        domain, len(items),
        int(sum(len(i.summary or "") for i in items) / max(len(items), 1)),
    )
    user_prompt = make_user_prompt(domain, items)
    raw = await claude_client.complete(SYSTEM_PROMPT, user_prompt)
    results = _parse_response(raw, fetched_by_url)
    logger.info("Domain '%s' → %d synthesized items", domain, len(results))
    return results


async def synthesize(items: list[FetchedItem]) -> list[SynthesizedItem]:
    """Synthesize ranked FetchedItems into narrative SynthesizedItems via Claude."""
    if not items:
        return []

    groups = _group_by_domain(items)
    tasks = [_synthesize_domain(domain, domain_items) for domain, domain_items in groups.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output: list[SynthesizedItem] = []
    for domain, result in zip(groups.keys(), results):
        if isinstance(result, Exception):
            logger.error("Synthesis failed for domain '%s': %s", domain, result)
            continue
        output.extend(result)

    return output
