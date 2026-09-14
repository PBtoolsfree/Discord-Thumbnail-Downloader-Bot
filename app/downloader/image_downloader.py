import os
import uuid
import httpx
import magic
from app.security.ssrf import is_safe_url
from app.config import settings
from app.logging_config import logger

class DownloadError(Exception):
    pass

class ImageDownloader:
    def __init__(self):
        # Create tmp directory if it doesn't exist
        self.tmp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)
        
        self.max_size_bytes = settings.max_image_size_mb * 1024 * 1024
        self.timeout = settings.request_timeout

        self.allowed_mimes = [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif"
        ]

    async def download_image(self, url: str) -> str:
        """
        Downloads an image securely.
        Returns the path to the downloaded file.
        Raises DownloadError on failure.
        """
        if not is_safe_url(url):
            raise DownloadError("URL failed security checks (SSRF / Invalid).")

        temp_filename = f"{uuid.uuid4().hex}.tmp"
        temp_filepath = os.path.join(self.tmp_dir, temp_filename)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                # We use stream to avoid loading huge files into memory if Content-Length is spoofed
                async with client.stream("GET", url) as response:
                    if response.status_code != 200:
                        raise DownloadError(f"HTTP {response.status_code} while fetching image.")

                    # Check Content-Length if provided
                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > self.max_size_bytes:
                        raise DownloadError("Image exceeds maximum allowed size.")

                    # Download in chunks
                    downloaded_size = 0
                    with open(temp_filepath, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            downloaded_size += len(chunk)
                            if downloaded_size > self.max_size_bytes:
                                raise DownloadError("Image exceeds maximum allowed size during streaming.")
                            f.write(chunk)

            # Verify file actually is an image using python-magic
            mime = magic.from_file(temp_filepath, mime=True)
            if mime not in self.allowed_mimes:
                raise DownloadError(f"Downloaded file has invalid MIME type: {mime}")

            # Rename file to have a proper extension
            ext = mime.split("/")[-1]
            if ext == "jpeg":
                ext = "jpg"
                
            final_filename = f"{uuid.uuid4().hex}.{ext}"
            final_filepath = os.path.join(self.tmp_dir, final_filename)
            os.rename(temp_filepath, final_filepath)
            
            return final_filepath

        except DownloadError:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            raise
        except Exception as e:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            logger.error(f"Failed to download image {url}: {e}")
            raise DownloadError("Failed to download image due to a network or processing error.")

downloader = ImageDownloader()
