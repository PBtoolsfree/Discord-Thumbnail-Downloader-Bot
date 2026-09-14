import pytest
from app.extractors.youtube import YouTubeExtractor
from app.extractors.vimeo import VimeoExtractor
from app.extractors.generic import GenericExtractor

@pytest.mark.asyncio
async def test_youtube_extractor_regex():
    extractor = YouTubeExtractor()
    assert extractor.can_handle("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
    assert extractor.can_handle("https://youtu.be/dQw4w9WgXcQ") is True
    assert extractor.can_handle("https://www.youtube.com/shorts/dQw4w9WgXcQ") is True
    assert extractor.can_handle("https://vimeo.com/123456") is False

@pytest.mark.asyncio
async def test_vimeo_extractor_regex():
    extractor = VimeoExtractor()
    assert extractor.can_handle("https://vimeo.com/12345678") is True
    assert extractor.can_handle("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is False
    
@pytest.mark.asyncio
async def test_generic_extractor_regex():
    extractor = GenericExtractor()
    assert extractor.can_handle("https://example.com") is True
    assert extractor.can_handle("http://example.com") is True
    assert extractor.can_handle("ftp://example.com") is False
