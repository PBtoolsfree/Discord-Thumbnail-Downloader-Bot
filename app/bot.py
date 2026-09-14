"""
Main discord bot initialization.
"""
import discord
from discord.ext import commands
import asyncio
from app.config import settings
from app.logging_config import logger
from app.cache.cache import cache

class PBThumbnailBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Required to read URLs from messages
        
        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Called once when the bot starts."""
        await cache.init_db()
        
        # Load cogs
        await self.load_extension("app.cogs.admin")
        await self.load_extension("app.cogs.listener")
        
        # Sync slash commands if needed
        # In a real app we might sync to a specific guild for faster updates
        try:
            if settings.discord_guild_id and settings.discord_guild_id.isdigit():
                guild = discord.Object(id=int(settings.discord_guild_id))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
            else:
                await self.tree.sync()
            logger.info("Slash commands synced.")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

    async def on_ready(self):
        logger.info(f"🟢 Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

def start_bot():
    if not settings.discord_token:
        logger.error("No Discord token provided. Please run the setup wizard or set DISCORD_TOKEN.")
        return
        
    bot = PBThumbnailBot()
    bot.run(settings.discord_token, log_handler=None)

if __name__ == "__main__":
    start_bot()
