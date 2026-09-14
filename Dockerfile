FROM python:3.12-slim

# Create a non-root user
RUN groupadd -r pbuser && useradd -r -g pbuser pbuser

# Set work directory
WORKDIR /app

# Install system dependencies (libmagic for python-magic)
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p data tmp \
    && chown -R pbuser:pbuser /app

# Copy project files
COPY app/ app/
COPY VERSION .

# Switch to non-root user
USER pbuser

# Expose Web Setup port
EXPOSE 8080

# Use a shell script to run both FastAPI and Discord Bot, or handle via docker-compose overrides
# Here we'll start just the bot by default. We can map command in compose to start setup too if needed.
# But for simplicity, we'll run a custom entrypoint or just the bot.
CMD ["python", "-m", "app.bot"]
