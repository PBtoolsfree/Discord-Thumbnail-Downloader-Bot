import re
import httpx
from app.extractors.base import BaseExtractor, ThumbnailResult, ExtractionError
from app.config import settings
from app.logging_config import logger

class VimeoExtractor(BaseExtractor):
    VIMEO_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)')

    def can_handle(self, url: str) -> bool:
        return bool(self.VIMEO_REGEX.search(url))

    async def extract(self, url: str) -> ThumbnailResult:
        match = self.VIMEO_REGEX.search(url)
        if not match:
            raise ExtractionError("Could not extract Vimeo video ID.")
            
        video_id = match.group(1)
        
        oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_id}"
        
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                res = await client.get(oembed_url)
                if res.status_code != 200:
                    raise ExtractionError(f"Vimeo API returned {res.status_code}")
                
                data = res.json()
                title = data.get("title", "Vimeo Video")
                thumbnail_url = data.get("thumbnail_url")
                
                if not thumbnail_url:
                    raise ExtractionError("No thumbnail URL provided by Vimeo API.")
                    
                # Get the highest resolution if possible by stripping dimensions
                # e.g., https://i.vimeocdn.com/video/123456_295x166.webp
                thumbnail_url = re.sub(r'_\d+x\d+', '', thumbnail_url)
                
                return ThumbnailResult(
                    platform="Vimeo",
                    title=title,
                    thumbnail_url=thumbnail_url
                )
                
        except ExtractionError:
            raise
        except Exception as e:
            logger.warning(f"Vimeo extraction failed: {e}")
            raise ExtractionError("Failed to fetch Vimeo metadata.")
