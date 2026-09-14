import os
import aiosqlite
from datetime import date
from app.logging_config import logger

class UserDatabase:
    def __init__(self):
        self.db_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "users.sqlite3")
        
        # Plan Limits (Thumbnails per day)
        self.limits = {
            "free": 5,
            "medium": 50,
            "unlimited": 999999999
        }

    async def init_db(self):
        """Initializes the users and usage tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    tier TEXT DEFAULT 'free'
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS usage (
                    user_id TEXT,
                    use_date TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, use_date)
                )
            ''')
            await db.commit()
            logger.info("User DB initialized.")

    async def get_user_tier(self, user_id: str) -> str:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT tier FROM users WHERE user_id = ?', (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else "free"
        except Exception as e:
            logger.error(f"Error reading user tier: {e}")
            return "free"

    async def set_user_tier(self, user_id: str, tier: str) -> bool:
        if tier not in self.limits:
            return False
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR REPLACE INTO users (user_id, tier) VALUES (?, ?)',
                    (user_id, tier)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting user tier: {e}")
            return False

    async def get_today_usage(self, user_id: str) -> int:
        today = date.today().isoformat()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT count FROM usage WHERE user_id = ? AND use_date = ?', (user_id, today)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error reading usage: {e}")
            return 0

    async def increment_usage(self, user_id: str, amount: int = 1) -> bool:
        today = date.today().isoformat()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Insert 0 if not exists
                await db.execute(
                    'INSERT OR IGNORE INTO usage (user_id, use_date, count) VALUES (?, ?, 0)',
                    (user_id, today)
                )
                # Increment
                await db.execute(
                    'UPDATE usage SET count = count + ? WHERE user_id = ? AND use_date = ?',
                    (amount, user_id, today)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")
            return False

    async def can_process(self, user_id: str, requested_amount: int) -> tuple[bool, int, str]:
        """
        Returns (is_allowed, remaining, tier)
        """
        tier = await self.get_user_tier(user_id)
        limit = self.limits.get(tier, self.limits["free"])
        
        usage = await self.get_today_usage(user_id)
        remaining = max(0, limit - usage)
        
        return (remaining >= requested_amount), remaining, tier

user_db = UserDatabase()
