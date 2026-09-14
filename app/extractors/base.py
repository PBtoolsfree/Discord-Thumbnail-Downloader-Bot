from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class ThumbnailResult:
    platform: str
    title: Optional[str]
    thumbnail_url: str

class ExtractionError(Exception):
    pass

class BaseExtractor(ABC):
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Returns True if this extractor can process the URL."""
        pass

    @abstractmethod
    async def extract(self, url: str) -> ThumbnailResult:
        """
        Extracts thumbnail metadata from the URL.
        Raises ExtractionError if extraction fails.
        """
        pass
