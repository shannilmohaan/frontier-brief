import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem
from app.services.ranker import classify_domains

logger = logging.getLogger(__name__)

# (rss_url, source_name, content_type)
FEEDS: list[tuple[str, str, str]] = [
    # Official AI lab blogs — Tier 1
    ("https://openai.com/news/rss.xml",                         "OpenAI",               "blog"),
    # Anthropic: no public RSS; use their newsletter via Substack
    ("https://www.anthropic.com/rss.xml",                       "Anthropic",            "blog"),
    # Google DeepMind blog RSS (alternate path)
    ("https://deepmind.google/blog/rss",                        "Google DeepMind",      "blog"),
    # Meta AI moved their blog — try engineering blog
    ("https://engineering.fb.com/category/ml-applications/feed/", "Meta AI",           "blog"),
    # Microsoft AI: bot-blocked on direct feed; skip for now
    # Mistral AI Ghost CMS — standard Ghost RSS path
    ("https://mistral.ai/rss/",                                 "Mistral AI Blog",      "blog"),
    ("https://huggingface.co/blog/feed.xml",                    "Hugging Face Blog",    "blog"),
    # Engineering / ecosystem
    ("https://aws.amazon.com/blogs/machine-learning/feed/",     "AWS ML Blog",          "blog"),
    ("https://blog.langchain.dev/rss/",                         "LangChain Blog",       "blog"),
    # Curated newsletters
    ("https://importai.substack.com/feed",                      "Import AI",            "newsletter"),
    ("https://magazine.sebastianraschka.com/feed",              "Ahead of AI",          "newsletter"),
    ("https://lastweekin.ai/feed",                              "Last Week in AI",      "newsletter"),
    # Ben's Bites moved to Beehiiv
    ("https://bensbites.beehiiv.com/feed",                      "Ben's Bites",          "newsletter"),
    ("https://www.interconnects.ai/feed",                       "Interconnects",        "newsletter"),
    # The Rundown AI on Beehiiv
    ("https://therundown.beehiiv.com/feed",                     "The Rundown AI",       "newsletter"),
    # Learning / course announcements
    # DeepLearning.AI The Batch newsletter
    ("https://www.deeplearning.ai/the-batch/rss/",              "DeepLearning.AI Blog", "newsletter"),
    ("https://www.fast.ai/index.xml",                           "fast.ai",              "blog"),
]

_HTML_TAG = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _HTML_TAG.sub(" ", text).strip()


def _parse_entry_date(entry: dict) -> datetime | None:  # type: ignore[type-arg]
    if entry.get("published_parsed"):
        try:
            return datetime(*entry["published_parsed"][:6], tzinfo=timezone.utc)
        except Exception:
            pass
    if entry.get("published"):
        try:
            return parsedate_to_datetime(entry["published"])
        except Exception:
            pass
    if entry.get("updated_parsed"):
        try:
            return datetime(*entry["updated_parsed"][:6], tzinfo=timezone.utc)
        except Exception:
            pass
    return None


class RssFeedFetcher(BaseFetcher):
    def __init__(self, window_hours: int = 168) -> None:
        self._window_hours = window_hours

    async def fetch(self) -> list[FetchedItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._window_hours)

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            results = await asyncio.gather(
                *[self._fetch_feed(client, url, name, ctype, cutoff) for url, name, ctype in FEEDS],
                return_exceptions=True,
            )

        items: list[FetchedItem] = []
        for (_, name, _), result in zip(FEEDS, results):
            if isinstance(result, Exception):
                logger.error("RSS fetch failed for %s: %s", name, result)
            else:
                items.extend(result)

        logger.info("RSS feeds: %d items in last %dh window", len(items), self._window_hours)
        return items

    async def _fetch_feed(
        self,
        client: httpx.AsyncClient,
        url: str,
        source_name: str,
        content_type: str,
        cutoff: datetime,
    ) -> list[FetchedItem]:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.text
        except Exception as exc:
            logger.warning("%s RSS unavailable: %s", source_name, exc)
            return []

        loop = asyncio.get_event_loop()
        try:
            feed = await loop.run_in_executor(None, feedparser.parse, content)
        except Exception as exc:
            logger.warning("%s RSS parse failed: %s", source_name, exc)
            return []

        items: list[FetchedItem] = []
        for entry in feed.entries:
            try:
                published_at = _parse_entry_date(entry)
                if published_at is None or published_at < cutoff:
                    continue

                title = _strip_html(entry.get("title", "")).strip()
                if not title:
                    continue

                link = entry.get("link", "")
                if not link:
                    continue

                raw_summary = (
                    entry.get("summary")
                    or (entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "")
                    or ""
                )
                summary = _strip_html(raw_summary)[:600]

                items.append(
                    FetchedItem(
                        title=title,
                        summary=summary,
                        source_name=source_name,
                        source_url=link,
                        domain_tags=classify_domains(f"{title} {summary}"),
                        published_at=published_at,
                        content_type=content_type,  # type: ignore[arg-type]
                    )
                )
            except Exception as exc:
                logger.warning("Skipping %s entry: %s", source_name, exc)
                continue

        logger.info("%s: %d items", source_name, len(items))
        return items
