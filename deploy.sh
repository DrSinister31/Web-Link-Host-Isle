#!/bin/bash
# Synix Park Deployment Script

set -e

echo "🚀 Starting Synix Park Infrastructure..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example to .env and fill in your secrets."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

# Validate required secrets
if [ -z "$DISCORD_TOKEN" ] || [ "$DISCORD_TOKEN" = "your_discord_bot_token_here" ]; then
    echo "❌ DISCORD_TOKEN not configured in .env"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Build and start containers
echo "📦 Building Docker image..."
docker build -t synix-park:latest .

echo "🐳 Starting services with docker-compose..."
docker compose up -d

echo "✅ Synix Park is live!"
echo "📡 API: http://localhost:8000"
echo "🎮 Check logs: docker compose logs -f"
