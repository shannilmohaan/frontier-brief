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
    # === Official AI lab blogs (Tier 1) ===
    ("https://openai.com/news/rss.xml",                                    "OpenAI",                "blog"),
    ("https://blog.google/technology/ai/rss/",                             "Google AI Blog",        "blog"),
    ("https://aws.amazon.com/blogs/machine-learning/feed/",                "AWS ML Blog",           "blog"),
    ("https://huggingface.co/blog/feed.xml",                               "Hugging Face Blog",     "blog"),
    ("https://cloudblog.withgoogle.com/products/ai-machine-learning/rss",  "Google Cloud AI",       "blog"),
    ("https://developer.nvidia.com/blog/feed/",                            "NVIDIA Developer Blog", "blog"),

    # === High-signal practitioner blogs (Tier 1 independent) ===
    ("https://simonwillison.net/atom/everything/",                         "Simon Willison",        "blog"),
    ("https://huyenchip.com/feed.xml",                                     "Chip Huyen",            "blog"),
    # Eugene Yan: Hugo blog — /index.xml is the standard Hugo feed path
    ("https://eugeneyan.com/index.xml",                                    "Eugene Yan",            "blog"),
    # Hamel Husain: Quarto blog — /index.xml is the standard Quarto feed path
    ("https://hamel.dev/index.xml",                                        "Hamel Husain",          "blog"),
    # Lilian Weng: OpenAI researcher, GitHub Pages Hugo blog
    ("https://lilianweng.github.io/index.xml",                             "Lilian Weng",           "blog"),
    # Jason Liu: instructor library author, AI engineering practitioner
    ("https://jxnl.co/feed.xml",                                           "Jason Liu",             "blog"),
    # AI Snake Oil: Princeton researchers, rigorous AI analysis
    ("https://aisnakeoil.substack.com/feed",                               "AI Snake Oil",          "blog"),

    # === Framework / ecosystem blogs (Tier 2 vendor) ===
    ("https://blog.langchain.dev/rss/",                                    "LangChain Blog",        "blog"),
    # LlamaIndex blog: blog.llamaindex.ai/rss/ returns 404; try alternate path
    ("https://www.llamaindex.ai/blog/rss.xml",                             "LlamaIndex Blog",       "blog"),

    # === Curated newsletters ===
    ("https://importai.substack.com/feed",                                 "Import AI",             "newsletter"),
    ("https://magazine.sebastianraschka.com/feed",                         "Ahead of AI",           "newsletter"),
    ("https://www.latent.space/feed",                                      "Latent Space",          "newsletter"),
    ("https://www.interconnects.ai/feed",                                  "Interconnects",         "newsletter"),
    ("https://lastweekin.ai/feed",                                         "Last Week in AI",       "newsletter"),
    ("https://bensbites.beehiiv.com/feed.xml",                             "Ben's Bites",           "newsletter"),

    # === Industry analysis (high signal, not noise) ===
    # TechCrunch removed — industry noise, wrong audience
    ("https://a16z.com/feed/",                                             "a16z AI",               "blog"),
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
