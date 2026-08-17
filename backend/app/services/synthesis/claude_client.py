import asyncio
import logging

import anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-5"
_MAX_TOKENS = 4096
_TIMEOUT_SECONDS = 90.0

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def complete(system: str, user: str) -> str:
    """Call Claude and return the text content from the response."""
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
    logger.debug("Claude response: stop_reason=%r blocks=%r", message.stop_reason, blocks)

    # Claude 5 may include thinking blocks before the text block — find by type attribute
    text_block = next(
        (b for b in blocks if getattr(b, "type", None) == "text"),
        None,
    )
    if text_block is None:
        raise ValueError(
            f"No text block in Claude response; stop_reason={message.stop_reason!r} blocks={blocks!r}"
        )
    text = getattr(text_block, "text", None)
    if text is None:
        raise ValueError(
            f"Claude text block has null text; stop_reason={message.stop_reason!r}"
        )
    if not text.strip():
        logger.warning("Claude returned empty text; stop_reason=%r — treating as no items", message.stop_reason)
        return "[]"
    return text
