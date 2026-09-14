import discord
from discord import app_commands
from discord.app_commands import Choice
from app.cache.user_db import user_db
from discord.ext import commands
from app.config import settings
from app.logging_config import logger

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    def is_admin(self, interaction: discord.Interaction) -> bool:
        """Check if user has admin permissions."""
        return interaction.permissions.administrator

    @app_commands.command(name="status", description="Check bot status")
    @app_commands.default_permissions(administrator=True)
    async def status(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You need administrator permissions.", ephemeral=True)
            return

        with open("VERSION", "r") as f:
            version = f.read().strip()
            
        channel_status = "Configured" if settings.thumbnail_channel_id else "Not Configured"
        
        msg = (
            f"🟢 **PB Thumbnail Bot**\n"
            f"**Status:** Online\n"
            f"**Server:** Connected ({interaction.guild.name if interaction.guild else 'DMs'})\n"
            f"**Thumbnail Channel:** {channel_status}\n"
            f"**Cache:** Active\n"
            f"**Version:** {version}\n"
        )
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="help", description="Show help information")
    @app_commands.default_permissions(administrator=True)
    async def help(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You need administrator permissions.", ephemeral=True)
            return

        msg = (
            "**PB Thumbnail Bot Help**\n"
            "`/status` - Check if the bot is running properly.\n"
            "`/config` - Check current bot limits.\n"
            "`/setchannel` - Set the thumbnail channel ID in `.env` (Currently requires a manual restart to apply if changed via slash, use Web setup instead).\n"
            "`/test` - Test if the bot can read from the configured channel.\n"
        )
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="config", description="Show bot configuration limits")
    @app_commands.default_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You need administrator permissions.", ephemeral=True)
            return
            
        msg = (
            f"**Bot Limits:**\n"
            f"Max URLs per message: {settings.max_urls_per_message}\n"
            f"Max Image Size: {settings.max_image_size_mb} MB\n"
            f"Cache TTL: {settings.cache_ttl_hours} Hours\n"
            f"Max Concurrent DLs: {settings.max_concurrent_downloads}\n"
        )
        await interaction.response.send_message(msg, ephemeral=True)
        
    @app_commands.command(name="test", description="Test if bot is correctly configured")
    @app_commands.default_permissions(administrator=True)
    async def test(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You need administrator permissions.", ephemeral=True)
            return
            
        if not settings.thumbnail_channel_id:
            await interaction.response.send_message("❌ Thumbnail channel is not configured in settings.", ephemeral=True)
            return
            
        try:
            channel_id = int(settings.thumbnail_channel_id)
            channel = self.bot.get_channel(channel_id)
            if channel:
                await interaction.response.send_message(f"✅ Found configured channel: <#{channel_id}>", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Could not find channel with ID {channel_id}. Is the bot invited to the server and does it have view permissions?", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Thumbnail channel ID is invalid.", ephemeral=True)

    @app_commands.command(name="tier_set", description="Admin: Set a user's premium tier")
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(tier=[
        Choice(name="Free (5/day)", value="free"),
        Choice(name="Medium (50/day)", value="medium"),
        Choice(name="Unlimited", value="unlimited"),
    ])
    async def tier_set(self, interaction: discord.Interaction, member: discord.Member, tier: Choice[str]):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You need administrator permissions.", ephemeral=True)
            return
            
        success = await user_db.set_user_tier(str(member.id), tier.value)
        if success:
            await interaction.response.send_message(f"✅ Successfully set **{member.display_name}** to **{tier.value.upper()}** tier.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Failed to set tier.", ephemeral=True)

    @app_commands.command(name="tier_view", description="Admin: View a user's tier and usage")
    @app_commands.default_permissions(administrator=True)
    async def tier_view(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You need administrator permissions.", ephemeral=True)
            return
            
        tier = await user_db.get_user_tier(str(member.id))
        usage = await user_db.get_today_usage(str(member.id))
        limit = user_db.limits.get(tier, 5)
        
        limit_display = "∞" if tier == "unlimited" else limit
        await interaction.response.send_message(f"👤 **{member.display_name}**\n**Tier:** {tier.upper()}\n**Today's Usage:** {usage} / {limit_display}", ephemeral=True)

    @app_commands.command(name="limits", description="View your remaining daily thumbnail downloads")
    async def limits(self, interaction: discord.Interaction):
        tier = await user_db.get_user_tier(str(interaction.user.id))
        usage = await user_db.get_today_usage(str(interaction.user.id))
        limit = user_db.limits.get(tier, 5)
        
        if tier == "unlimited":
            msg = "🌟 **Your Plan:** UNLIMITED\nYou have no download limits! Enjoy!"
        else:
            remaining = max(0, limit - usage)
            msg = f"📊 **Your Plan:** {tier.upper()}\n**Today's Usage:** {usage} / {limit}\n**Remaining:** {remaining}"
            
        await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
