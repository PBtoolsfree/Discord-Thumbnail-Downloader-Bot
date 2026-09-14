import os
import secrets
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from app.config import settings

app = FastAPI(title="PB Thumbnail Bot Setup")
security = HTTPBasic()

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, settings.setup_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, username: str = Depends(get_current_username)):
    if not settings.setup_enabled:
        return HTMLResponse("<h1>Setup is disabled in .env</h1>")
        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings,
        "success": False
    })

@app.post("/", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    discord_token: str = Form(""),
    discord_client_id: str = Form(""),
    discord_guild_id: str = Form(""),
    thumbnail_channel_id: str = Form(""),
    max_urls_per_message: int = Form(5),
    max_image_size_mb: int = Form(8),
    cache_ttl_hours: int = Form(24),
    username: str = Depends(get_current_username)
):
    if not settings.setup_enabled:
        return HTMLResponse("<h1>Setup is disabled in .env</h1>")

    # Save to .env
    env_path = os.path.join(os.getcwd(), ".env")
    
    env_content = f"""# Discord Bot Configuration
DISCORD_TOKEN={discord_token}
DISCORD_CLIENT_ID={discord_client_id}
DISCORD_GUILD_ID={discord_guild_id}
THUMBNAIL_CHANNEL_ID={thumbnail_channel_id}

# Limits & Features
MAX_URLS_PER_MESSAGE={max_urls_per_message}
MAX_IMAGE_SIZE_MB={max_image_size_mb}
CACHE_TTL_HOURS={cache_ttl_hours}
MAX_CONCURRENT_DOWNLOADS=3
REQUEST_TIMEOUT=15

# Logging
LOG_LEVEL=INFO

# Web Setup Wizard
SETUP_ENABLED=true
SETUP_PASSWORD={settings.setup_password}
SETUP_PORT={settings.setup_port}
"""
    with open(env_path, "w") as f:
        f.write(env_content)
        
    # Reload settings in current process for UI feedback
    settings.discord_token = discord_token
    settings.discord_client_id = discord_client_id
    settings.discord_guild_id = discord_guild_id
    settings.thumbnail_channel_id = thumbnail_channel_id
    settings.max_urls_per_message = max_urls_per_message
    settings.max_image_size_mb = max_image_size_mb
    settings.cache_ttl_hours = cache_ttl_hours

    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings,
        "success": True,
        "message": "Configuration saved successfully! Please restart the bot container to apply."
    })

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "discord": "configured" if settings.discord_token else "unconfigured",
        "setup_enabled": settings.setup_enabled
    }

def start_web():
    uvicorn.run("app.web.setup:app", host="0.0.0.0", port=settings.setup_port, log_level="info")

if __name__ == "__main__":
    start_web()
