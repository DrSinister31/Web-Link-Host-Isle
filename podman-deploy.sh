#!/bin/bash
# Sinister's Park - Podman Autonomous AI Operator Deployment
# Run on Linux: bash ~/podman-operator/deploy.sh

set -e

OPERATOR_DIR="$HOME/podman-operator"
SYNIX_REPO="https://github.com/yourusername/sinister-park"  # Update with actual repo

echo ""
echo "=========================================="
echo " SINISTER'S PARK PODMAN DEPLOYMENT"
echo "=========================================="
echo ""

# Step 1: Check for Podman
echo "[1/7] Checking for Podman installation..."
if ! command -v podman &> /dev/null; then
    echo "❌ Podman not found. Installing..."
    if [ -f /etc/debian_version ]; then
        sudo apt update && sudo apt install -y podman podman-compose
    elif [ -f /etc/redhat-release ]; then
        sudo dnf install -y podman podman-compose
    else
        echo "❌ Unsupported Linux distribution"
        exit 1
    fi
fi
echo "✅ Podman found: $(podman --version)"

# Step 2: Create directories
echo "[2/7] Creating project directories..."
mkdir -p "$OPERATOR_DIR"/{ollama_data,open-webui_data,synix_root,postgres_data}
echo "✅ Directories created at: $OPERATOR_DIR"

# Step 3: Clone/Update Sinister's Park code
echo "[3/7] Cloning Sinister's Park repository..."
if [ -d "$OPERATOR_DIR/synix_root/.git" ]; then
    echo "Repository exists, pulling latest..."
    cd "$OPERATOR_DIR/synix_root" && git pull origin main
else
    echo "Cloning fresh repository..."
    git clone "$SYNIX_REPO" "$OPERATOR_DIR/synix_root" || echo "⚠️  Could not clone. Ensure git is installed and repo exists."
fi
cd "$OPERATOR_DIR"

# Step 4: Set up podman-compose.yml (if not exists)
echo "[4/7] Configuring podman-compose.yml..."
if [ ! -f "$OPERATOR_DIR/podman-compose.yml" ]; then
    echo "Creating podman-compose.yml..."
    cat > "$OPERATOR_DIR/podman-compose.yml" << 'EOF'
version: '3.8'
services:
  ollama:
    image: docker.io/ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: synix-ai-operator
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - ENABLE_TOOLS=true
      - WEBUI_AUTH=true
    volumes:
      - ./open-webui_data:/app/backend/data
      - ./synix_root:/app/files
    depends_on:
      - ollama
    restart: unless-stopped
EOF
fi
echo "✅ podman-compose.yml configured"

# Step 5: Start services
echo "[5/7] Starting Podman services..."
podman-compose up -d
sleep 5

# Step 6: Verify services
echo "[6/7] Verifying services..."
if podman ps | grep -q "ollama"; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama failed to start"
    podman-compose logs ollama
    exit 1
fi

if podman ps | grep -q "synix-ai-operator"; then
    echo "✅ Open WebUI is running"
else
    echo "❌ Open WebUI failed to start"
    podman-compose logs synix-ai-operator
    exit 1
fi

# Step 7: Print access information
echo "[7/7] Deployment complete!"
echo ""
echo "=========================================="
echo " ACCESS YOUR AI OPERATOR"
echo "=========================================="
echo ""
echo "🌐 Open WebUI:    http://localhost:3000"
echo "📡 Ollama API:    http://localhost:11434"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Create an admin account"
echo "3. Go to Settings > Models and pull 'llama2' (or 'llama3.2')"
echo "4. Enable Tools in Settings > Tools"
echo "5. Start using the AI to review and modify your code!"
echo ""
echo "View logs:"
echo "  podman-compose logs -f"
echo ""
echo "Stop services:"
echo "  podman-compose down"
echo ""
