import socket
import ipaddress
from urllib.parse import urlparse
from app.logging_config import logger

class SSRFError(Exception):
    pass

def is_safe_url(url: str) -> bool:
    """
    Checks if the URL is safe to fetch (prevents SSRF).
    - Must be http or https
    - Must not resolve to a private/local/link-local IP address
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            logger.warning(f"SSRF block: Invalid scheme '{parsed.scheme}' for URL: {url}")
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Attempt to resolve the hostname
        # Note: socket.getaddrinfo might block, but usually very fast.
        # Ideally this is async, but for a simple bot socket block is acceptable or use aiosns.
        # We will just use the basic sync resolver since it's cached by OS typically.
        addr_info = socket.getaddrinfo(hostname, None)
        
        for result in addr_info:
            ip_str = result[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                logger.warning(f"SSRF block: Hostname '{hostname}' resolved to private IP '{ip_str}'")
                return False
                
        return True
    except socket.gaierror:
        # If we can't resolve it, we can't fetch it, so it's "unsafe/invalid"
        logger.warning(f"DNS Resolution failed for URL: {url}")
        return False
    except ValueError:
        # Invalid IP address parsed
        return False
    except Exception as e:
        logger.error(f"Unexpected error in SSRF check: {e}")
        return False
