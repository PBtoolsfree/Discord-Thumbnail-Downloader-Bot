import re
import httpx
from urllib.parse import urlparse, parse_qs
from app.extractors.base import BaseExtractor, ThumbnailResult, ExtractionError
from app.config import settings
from app.logging_config import logger
from app.security.ssrf import is_safe_url

class YouTubeExtractor(BaseExtractor):
    # Regex to match youtube.com and youtu.be URLs
    # Also handles shorts and standard watch endpoints
    YT_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/|live\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})')
    
    def can_handle(self, url: str) -> bool:
        return bool(self.YT_REGEX.search(url))

    async def extract(self, url: str) -> ThumbnailResult:
        match = self.YT_REGEX.search(url)
        if not match:
            raise ExtractionError("Could not extract YouTube video ID.")
            
        video_id = match.group(1)
        
        # Max resolution thumbnail is often at maxresdefault.jpg
        # Fallbacks: hqdefault.jpg, mqdefault.jpg, default.jpg
        best_thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        fallback_thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        
        # Try fetching oEmbed data for title
        title = "YouTube Video"
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                res = await client.get(oembed_url)
                if res.status_code == 200:
                    data = res.json()
                    title = data.get("title", title)
                    # We can also use oembed thumbnail if desired, but we usually want maxres
        except Exception as e:
            logger.warning(f"YouTube oEmbed fetch failed: {e}")
            
        # We assume maxresdefault works. If downloader fails, we could potentially fallback,
        # but returning best_thumbnail directly is standard. 
        # Alternatively, verify it here before returning.
        return ThumbnailResult(
            platform="YouTube",
            title=title,
            thumbnail_url=best_thumbnail
        )
