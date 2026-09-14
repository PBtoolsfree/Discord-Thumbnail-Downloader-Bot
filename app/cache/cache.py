import os
import time
import aiosqlite
from app.config import settings
from app.logging_config import logger

class ThumbnailCache:
    def __init__(self):
        self.db_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "cache.sqlite3")
        self.ttl_seconds = settings.cache_ttl_hours * 3600

    async def init_db(self):
        """Initializes the cache table."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    url TEXT PRIMARY KEY,
                    timestamp INTEGER
                )
            ''')
            await db.commit()
            logger.info("Cache DB initialized.")

    async def is_cached(self, url: str) -> bool:
        """
        Checks if the URL is in the cache and valid.
        """
        now = int(time.time())
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT timestamp FROM requests WHERE url = ?', (url,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        timestamp = row[0]
                        if now - timestamp < self.ttl_seconds:
                            return True
                        else:
                            # Expired
                            await db.execute('DELETE FROM requests WHERE url = ?', (url,))
                            await db.commit()
            return False
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return False

    async def set_cached(self, url: str):
        """
        Saves the URL into the cache.
        """
        now = int(time.time())
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR REPLACE INTO requests (url, timestamp) VALUES (?, ?)',
                    (url, now)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    async def cleanup(self):
        """
        Deletes expired cache entries.
        """
        now = int(time.time())
        cutoff = now - self.ttl_seconds
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('DELETE FROM requests WHERE timestamp < ?', (cutoff,))
                await db.commit()
                logger.info("Cache cleanup executed.")
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")

cache = ThumbnailCache()
