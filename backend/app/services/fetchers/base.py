from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


ContentType = Literal["video", "paper", "newsletter", "blog", "social", "discussion", "podcast"]


@dataclass
class FetchedItem:
    title: str
    summary: str
    source_name: str
    source_url: str
    domain_tags: list[str]
    published_at: datetime
    content_type: ContentType
    social_score: float = field(default=0.0)
    thumbnail_url: str | None = field(default=None)


class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self) -> list[FetchedItem]:
        """Fetch items from the source. Must not raise — return [] on failure."""
