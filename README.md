# PB Thumbnail Bot

A production-ready Discord bot for automatically downloading and sending thumbnails from video links (YouTube, Vimeo, and generic websites) pasted in a specific channel.

## Features
- **Automatic Thumbnail Extraction**: Gets the highest quality thumbnail available legally without bypassing DRM or authentication.
- **Supported Platforms**: YouTube, Vimeo, Generic Open Graph / Twitter Card metadata.
- **SSRF Protection**: Blocks downloads from private IPs and localhost.
- **Web Setup Dashboard**: Easy configuration through a web interface.
- **Dockerized**: Easy to deploy on Oracle Cloud Free Tier or any VPS.
- **Resource Efficient**: Asynchronous, lightweight, with caching to prevent duplicate downloads.
- **Rate Limits**: Configurable concurrency and file size limits.
- **Premium Tiers & Monetization**: Built-in daily usage limits (Free, Medium, Unlimited) allowing you to monetize access.

## Requirements
- Docker and Docker Compose
- Discord Bot Token

## Discord Bot Creation Guide
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name.
3. Go to the **Bot** tab and click **Add Bot**.
4. **Important**: Under **Privileged Gateway Intents**, enable **Message Content Intent** (so the bot can read messages containing links).
5. Go to the **OAuth2 > URL Generator** tab.
6. Select the `bot` and `applications.commands` scopes.
7. Select the following Bot Permissions: `Send Messages`, `Attach Files`, `Embed Links`, `Read Message History`, `View Channels`.
8. Copy the generated URL and paste it in your browser to invite the bot to your server.
9. Go back to the **Bot** tab and copy your **Token**. Keep it safe!

## One-Click Installation (Linux / Oracle Cloud)

### Prerequisites (For fresh Ubuntu/Debian servers)
If you are running this on a brand new VPS, install Git and Docker first:
```bash
sudo apt update && sudo apt install git -y
curl -fsSL https://get.docker.com | sudo sh
```

1. Clone the repository:
   ```bash
   git clone https://github.com/PBtoolsfree/Discord-Thumbnail-Downloader-Bot.git
   cd Discord-Thumbnail-Downloader-Bot
   ```
2. Run the installer:
   ```bash
   bash install.sh
   ```
3. Look at the output. It will give you a temporary password for the setup dashboard.
4. Go to the Setup Dashboard URL shown in your terminal output (e.g., `http://YOUR_SERVER_IP:8080`) in your web browser.
5. Login with username `admin` and the generated password.
6. Enter your Discord Bot Token and settings, and click Save.
7. Restart the bot container to apply:
   ```bash
   docker compose restart bot
   ```

## Web Dashboard Note
Once configured, it's highly recommended to disable the setup dashboard by setting `SETUP_ENABLED=false` in `.env` and restarting.

## Bot Commands

### Admin Commands (Requires Administrator Permission)
- `/status` - Check bot status
- `/config` - View current global configuration limits
- `/tier_set @User [tier]` - Upgrade a user to a premium tier (`free`, `medium`, `unlimited`)
- `/tier_view @User` - Check a user's current tier and daily usage
- `/test` - Test if the channel is properly configured
- `/help` - View help

### User Commands (Available to everyone)
- `/limits` - View your active plan, today's usage, and remaining downloads

## Updating
Run the update script safely:
```bash
bash update.sh
```

## Security
This bot was designed with security in mind:
- Server-Side Request Forgery (SSRF) protection against private IPs.
- Temporary files are properly named with UUIDs and deleted.
- Content types are checked via libmagic instead of trusting file extensions.
- No shell command injection risks.

## License
MIT License.
