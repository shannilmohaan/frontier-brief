from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FetchedItem:
    title: str
    summary: str
    source_name: str
    source_url: str
    domain_tags: list[str]
    published_at: datetime
    content_type: str  # video | paper | newsletter | blog | social | discussion


class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self) -> list[FetchedItem]:
        """Fetch items from the source. Must not raise — return [] on failure."""
