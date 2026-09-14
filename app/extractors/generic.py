import httpx
from bs4 import BeautifulSoup
from app.extractors.base import BaseExtractor, ThumbnailResult, ExtractionError
from app.config import settings
from app.logging_config import logger
from app.security.ssrf import is_safe_url

class GenericExtractor(BaseExtractor):
    
    def can_handle(self, url: str) -> bool:
        """
        Generic extractor handles anything that is a safe URL.
        It relies on Open Graph or Twitter Card tags.
        """
        return is_safe_url(url)

    async def extract(self, url: str) -> ThumbnailResult:
        try:
            # Provide a normal user agent to avoid being blocked by simple bot protections
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True, headers=headers) as client:
                # Use stream to only fetch up to a certain size (e.g. 1MB of HTML) to prevent loading massive files
                async with client.stream("GET", url) as response:
                    if response.status_code != 200:
                        raise ExtractionError(f"HTTP {response.status_code}")
                    
                    content_type = response.headers.get("Content-Type", "")
                    if "text/html" not in content_type.lower():
                        # Direct image fallback? We could support it.
                        if "image/" in content_type.lower():
                            return ThumbnailResult(
                                platform="Direct Image",
                                title="Image Link",
                                thumbnail_url=url
                            )
                        raise ExtractionError(f"URL is not an HTML document or Image (Type: {content_type})")
                    
                    html_content = b""
                    chunk_size = 8192
                    max_html_size = 1024 * 1024 # 1 MB max for HTML parsing
                    downloaded = 0
                    
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        html_content += chunk
                        downloaded += len(chunk)
                        if downloaded > max_html_size:
                            break # We got enough HTML to parse head metadata

            soup = BeautifulSoup(html_content, "lxml") # lxml is fast
            
            # Find title
            title = None
            og_title = soup.find("meta", property="og:title")
            twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
            head_title = soup.find("title")
            
            if og_title and og_title.get("content"):
                title = og_title["content"]
            elif twitter_title and twitter_title.get("content"):
                title = twitter_title["content"]
            elif head_title and head_title.string:
                title = head_title.string.strip()
            
            # Find image
            image_url = None
            og_image = soup.find("meta", property="og:image")
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            
            if og_image and og_image.get("content"):
                image_url = og_image["content"]
            elif twitter_image and twitter_image.get("content"):
                image_url = twitter_image["content"]
                
            if not image_url:
                raise ExtractionError("No Open Graph or Twitter Card image found.")
            
            # Ensure the image URL is absolute
            if image_url.startswith("//"):
                parsed_url = httpx.URL(url)
                image_url = f"{parsed_url.scheme}:{image_url}"
            elif image_url.startswith("/"):
                parsed_url = httpx.URL(url)
                image_url = f"{parsed_url.scheme}://{parsed_url.host}{image_url}"
                
            return ThumbnailResult(
                platform="Website",
                title=title or "No Title",
                thumbnail_url=image_url
            )
            
        except ExtractionError:
            raise
        except Exception as e:
            logger.warning(f"Generic extraction failed for {url}: {e}")
            raise ExtractionError("Failed to fetch metadata from the URL.")
