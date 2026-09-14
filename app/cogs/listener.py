import re
import os
import asyncio
import discord
from discord.ext import commands
from app.config import settings
from app.logging_config import logger
from app.extractors import get_all_extractors
from app.extractors.base import ExtractionError
from app.downloader.image_downloader import downloader, DownloadError
from app.cache.cache import cache

URL_REGEX = re.compile(r'(https?://\S+)')

class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.extractors = get_all_extractors()
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_downloads)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot's own messages
        if message.author == self.bot.user:
            return

        # Ensure channel is configured and matches
        if not settings.thumbnail_channel_id or message.channel.id != settings.thumbnail_channel_id:
            return

        # Find URLs
        urls = URL_REGEX.findall(message.content)
        if not urls:
            return

        # Limit to max URLs
        if len(urls) > settings.max_urls_per_message:
            await message.reply(f"⚠️ Too many URLs! Processing first {settings.max_urls_per_message}.")
            urls = urls[:settings.max_urls_per_message]

        for url in urls:
            # We process them in asyncio tasks but rate limit via semaphore
            self.bot.loop.create_task(self.process_url(message, url))

    async def process_url(self, message: discord.Message, url: str):
        async with self.semaphore:
            if await cache.is_cached(url):
                logger.info(f"Skipping cached URL: {url}")
                return

            extractor = next((e for e in self.extractors if e.can_handle(url)), None)
            if not extractor:
                logger.info(f"No extractor found for URL: {url}")
                return

            status_msg = await message.reply(f"⏳ Processing {extractor.__class__.__name__} URL...")

            downloaded_file_path = None
            try:
                # 1. Extract thumbnail metadata
                result = await extractor.extract(url)
                logger.info(f"Extracted metadata: {result}")

                if not result.thumbnail_url:
                    raise ExtractionError("Thumbnail URL is empty.")

                # 2. Download thumbnail securely
                downloaded_file_path = await downloader.download_image(result.thumbnail_url)

                # 3. Upload to Discord
                file = discord.File(downloaded_file_path)
                
                embed = discord.Embed(
                    title=f"🎬 {result.title}",
                    description=f"Platform: **{result.platform}**\nSource: <{url}>",
                    color=discord.Color.green()
                )
                
                await message.reply(embed=embed, file=file)
                await status_msg.delete()

                # 4. Save to cache
                await cache.set_cached(url)

            except ExtractionError as e:
                logger.warning(f"Extraction failed for {url}: {e}")
                await status_msg.edit(content=f"❌ Thumbnail nahi mil paya bhai.\nReason: Platform ne request block kar di ya public data nahi hai.")
            except DownloadError as e:
                logger.warning(f"Download failed for {url}: {e}")
                await status_msg.edit(content=f"❌ Thumbnail download nahi ho paya.\nReason: Image bahut badi hai ya file invalid hai.")
            except Exception as e:
                logger.error(f"Unexpected error processing {url}: {e}")
                await status_msg.edit(content=f"❌ Kuch error aa gaya bhai.")
            finally:
                # Clean up local file
                if downloaded_file_path and os.path.exists(downloaded_file_path):
                    try:
                        os.remove(downloaded_file_path)
                    except Exception as e:
                        logger.error(f"Failed to delete temp file {downloaded_file_path}: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ListenerCog(bot))
