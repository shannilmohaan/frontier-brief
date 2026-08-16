import asyncio
import logging

import anthropic
from anthropic.types import TextBlock

from app.core.config import settings

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-5"
_MAX_TOKENS = 2048
_TIMEOUT_SECONDS = 30.0

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def complete(system: str, user: str) -> str:
    """Call Claude and return the text of the first content block."""
    try:
        message = await asyncio.wait_for(
            _get_client().messages.create(
                model=_MODEL,
                max_tokens=_MAX_TOKENS,
                system=system,
                messages=[{"role": "user", "content": user}],
            ),
            timeout=_TIMEOUT_SECONDS,
        )
    except anthropic.RateLimitError as exc:
        retry_after = exc.response.headers.get("retry-after", "unknown")
        logger.warning("Claude rate limit hit; retry-after=%s", retry_after)
        raise
    except anthropic.APIStatusError as exc:
        logger.error("Claude API error status=%s body=%s", exc.status_code, exc.body)
        raise

    blocks = message.content
    if not blocks or not isinstance(blocks[0], TextBlock):
        raise ValueError(f"Unexpected response content from Claude: {blocks!r}")
    return blocks[0].text
