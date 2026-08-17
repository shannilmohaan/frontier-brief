import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.core.config import settings
from app.db.models import DigestCycle, DigestItem, SourceItem
from app.services.fetchers.base import FetchedItem
from app.services.fetchers.podcast_rss import PodcastRssFetcher
from app.services.fetchers.rss_feed import RssFeedFetcher
from app.services.fetchers.youtube import YouTubeFetcher
from app.services.ranker import rank_and_cap, score_item
from app.services.synthesis.synthesizer import SynthesizedItem, synthesize

logger = logging.getLogger(__name__)


async def run_pipeline(cycle_id: uuid.UUID, session_factory) -> None:
    """Execute a full digest pipeline: fetch → rank → synthesize → persist.

    Uses two separate DB sessions so the pool connection is not held open
    during the Claude API call (which can take 30–60 seconds).
    """
    try:
        source_items_by_url, scores_by_url, all_items = await _fetch_and_persist_sources(
            cycle_id, session_factory
        )
        ranked = rank_and_cap(all_items, max_per_domain=settings.max_items_per_domain)
        # Drop items with too-thin summaries — feeds like Google News often give
        # "Publisher · 2 hours ago" as description; Claude needs real content.
        synthesizable = [item for item in ranked if item.summary and len(item.summary.strip()) >= 80]
        logger.info("Synthesizable after content-quality filter: %d / %d ranked", len(synthesizable), len(ranked))
        synthesized = await synthesize(synthesizable)  # External API — no DB connection held
        await _persist_digest_items(cycle_id, synthesized, source_items_by_url, scores_by_url, len(all_items), session_factory)
    except Exception as exc:
        logger.exception("Pipeline failed for cycle %s", cycle_id)
        try:
            async with session_factory() as session:
                cycle = await session.get(DigestCycle, cycle_id)
                if cycle:
                    cycle.status = "failed"
                    cycle.error_message = str(exc)[:500]
                    cycle.completed_at = datetime.now(timezone.utc)
                    await session.commit()
        except Exception:
            logger.exception("Could not mark cycle %s as failed in DB", cycle_id)


async def _fetch_and_persist_sources(
    cycle_id: uuid.UUID, session_factory
) -> tuple[dict[str, SourceItem], dict[str, float], list[FetchedItem]]:
    """Session 1: mark running, run fetchers, persist SourceItems, commit."""
    async with session_factory() as session:
        cycle = await session.get(DigestCycle, cycle_id)
        if cycle is None:
            raise ValueError(f"DigestCycle {cycle_id} not found")
        cycle.status = "running"
        await session.commit()

        fetchers = [
            RssFeedFetcher(window_hours=168),
            YouTubeFetcher(window_hours=168),
            PodcastRssFetcher(window_hours=168),
        ]
        raw_results = await asyncio.gather(*[f.fetch() for f in fetchers], return_exceptions=True)

        all_items: list[FetchedItem] = []
        for fetcher, result in zip(fetchers, raw_results):
            if isinstance(result, Exception):
                logger.error("Fetcher %s failed: %s", type(fetcher).__name__, result)
            else:
                all_items.extend(result)

        logger.info("Fetched %d items total", len(all_items))

        scores_by_url = {item.source_url: score_item(item) for item in all_items}

        # Deduplicate by URL and persist — UUIDs are Python-generated, available before flush
        source_items_by_url: dict[str, SourceItem] = {}
        for fetched in all_items:
            if fetched.source_url in source_items_by_url:
                continue
            si = SourceItem(
                cycle_id=cycle_id,
                source_name=fetched.source_name,
                source_url=fetched.source_url,
                title=fetched.title,
                raw_content=fetched.summary,
                content_type=fetched.content_type,
                domain_tags=fetched.domain_tags,
                published_at=fetched.published_at,
                thumbnail_url=fetched.thumbnail_url,
            )
            session.add(si)
            source_items_by_url[fetched.source_url] = si

        await session.commit()  # Releases DB connection before synthesis

    return source_items_by_url, scores_by_url, all_items


async def _persist_digest_items(
    cycle_id: uuid.UUID,
    synthesized: list[SynthesizedItem],
    source_items_by_url: dict[str, SourceItem],
    scores_by_url: dict[str, float],
    items_fetched: int,
    session_factory,
) -> None:
    """Session 2: persist DigestItems and mark cycle completed."""
    async with session_factory() as session:
        for synth in synthesized:
            source_item = source_items_by_url.get(synth.source_url)
            if source_item is None:
                logger.warning("No SourceItem for synthesized URL: %s", synth.source_url)
                continue
            session.add(
                DigestItem(
                    cycle_id=cycle_id,
                    source_item_id=source_item.id,
                    narrative=synth.narrative,
                    why_it_matters=synth.why_it_matters or None,
                    what_changed=synth.what_changed or None,
                    who_should_care=synth.who_should_care or None,
                    build_impact=synth.build_impact or None,
                    production_readiness=synth.production_readiness or None,
                    importance=synth.importance,
                    source_name=synth.source_name,
                    source_url=synth.source_url,
                    content_type=synth.content_type,
                    domain_tags=synth.domain_tags,
                    relevance_score=scores_by_url.get(synth.source_url, 0.0),
                )
            )

        cycle = await session.get(DigestCycle, cycle_id)
        if cycle:
            cycle.status = "completed"
            cycle.items_fetched = items_fetched
            cycle.items_synthesized = len(synthesized)
            cycle.completed_at = datetime.now(timezone.utc)

        await session.commit()
        logger.info("Cycle %s completed: %d items synthesized", cycle_id, len(synthesized))
