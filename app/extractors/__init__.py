"""
Extractors module for retrieving thumbnail URLs from various platforms.
"""
from typing import List
from app.extractors.base import BaseExtractor
from app.extractors.youtube import YouTubeExtractor
from app.extractors.vimeo import VimeoExtractor
from app.extractors.generic import GenericExtractor

def get_all_extractors() -> List[BaseExtractor]:
    """Returns an ordered list of extractors to try."""
    return [
        YouTubeExtractor(),
        VimeoExtractor(),
        GenericExtractor() # Always last as a fallback
    ]
