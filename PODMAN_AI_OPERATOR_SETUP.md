# Sinister's Park - Podman Autonomous AI Operator Setup

This guide sets up an autonomous AI operator using Podman that can read, modify, and manage your Sinister's Park codebase.

## Prerequisites

- Linux system (Ubuntu, Fedora, Debian, CentOS, etc.)
- sudo access
- ~10GB disk space for models and data

## Step 1: Install Podman and Podman-Compose

### For Debian/Ubuntu-based systems:

```bash
sudo apt update
sudo apt install -y podman podman-compose
```

### For Fedora/CentOS/RHEL-based systems:

```bash
sudo dnf install -y podman podman-compose
```

### Verify Installation:

```bash
podman --version
podman-compose --version
```

Expected output:
```
podman version 4.x.x
podman-compose version 1.x.x
```

## Step 2: Set Up Your Project Directory

Create a dedicated folder for the Podman operator:

```bash
# Create the main directory
mkdir -p ~/podman-operator
cd ~/podman-operator

# Create subdirectories for persistent data
mkdir -p ollama_data open-webui_data synix_root postgres_data
```

Directory structure:
```
~/podman-operator/
├── podman-compose.yml
├── ollama_data/              # Ollama models persist here
├── open-webui_data/          # AI settings and chat history
├── synix_root/               # Your Sinister's Park code
└── postgres_data/            # (Optional) Database persistence
```

## Step 3: Copy Your Code to synix_root

Copy your Sinister's Park source code to the `synix_root` directory:

```bash
# From your Windows system, copy the code to ~/podman-operator/synix_root/
# Or if on Linux already:
cp -r /path/to/synix_root/* ~/podman-operator/synix_root/
```

The AI operator will have direct read/write access to files in this directory.

## Step 4: Deploy Services with Podman-Compose

Start all services:

```bash
cd ~/podman-operator
podman-compose up -d
```

Verify services are running:

```bash
podman-compose ps
```

Expected output:
```
CONTAINER ID  IMAGE                                  COMMAND       CREATED        STATUS       PORTS
abc123        docker.io/ollama/ollama:latest         ollama serve  5 minutes ago  Up 5 min     0.0.0.0:11434->11434/tcp
def456        ghcr.io/open-webui/open-webui:main    bash start.sh 5 minutes ago  Up 5 min     0.0.0.0:3000->8080/tcp
```

## Step 5: Access the AI Operator

1. Open your browser: `http://localhost:3000`
2. Create an admin account (first time setup)
3. Go to **Settings > Models** and pull a model:
   - Type: `llama2` (fast, 4GB) or `llama3.2` (better, 7GB)
   - Click "Pull"
   - Wait for download (~5-10 minutes)

## Step 6: Configure AI Operator Tools

1. Go to **Settings > Tools**
2. Enable available tools:
   - File System (read/write access to `/app/files` = `synix_root`)
   - Web Search (if you add Google API key)
   - Calculator
3. Save settings

## Step 7: Give AI Access to Your Code

Once the model is loaded, you can:

1. **Read Code**: Prompt: "Read `/app/files/bridge/synix_bot_3.py`"
2. **Analyze**: "What does the link command do?"
3. **Modify**: "Update the `/link` command to validate Steam IDs using a regex"
4. **Create**: "Write a new file `/app/files/bridge/telemetry_handler.py` that logs player events"
5. **Test**: "Check if my code has any syntax errors"

## Example Autonomous Workflow

```
You: "Review the Discord bot code and suggest improvements for the /link command"

AI: "I've analyzed /app/files/bridge/synix_bot_3.py...
- The Steam ID validation uses only length check (17 digits)
- Suggestion: Add regex validation to ensure it's a valid format
- I'm updating the validation..."

AI writes: /app/files/bridge/synix_bot_3.py (updated)

You: "Rebuild the Docker image and test it"

AI: "I'll execute the rebuild..."
[Runs docker build commands via shell tools]
```

## Common Commands

### View Logs

```bash
# All services
podman-compose logs -f

# Specific service
podman logs ollama -f
podman logs synix-ai-operator -f
```

### Stop Services

```bash
podman-compose down
```

### Remove Everything and Start Fresh

```bash
podman-compose down -v
rm -rf ollama_data open-webui_data
podman-compose up -d
```

### Execute Commands in Container

```bash
# Run a command in the AI container
podman exec synix-ai-operator bash -c "ls -la /app/files"

# Access the AI container shell
podman exec -it synix-ai-operator bash
```

## Security Best Practices

⚠️ **Important**: The AI has read/write access to your entire `synix_root` directory.

1. **Review Changes**: Always review the AI's code modifications before committing
2. **Backup**: Keep backups of critical files
3. **Test**: Run tests after AI-generated changes
4. **Restrict Access**: Run on a secure network, don't expose ports publicly
5. **API Keys**: Never hardcode secrets; use environment variables

## Performance Optimization

### Use a Faster Model

Smaller, faster models:
- `tinyllama` - 636MB (fastest)
- `neural-chat` - 4GB (balanced)
- `llama2` - 4GB (good quality)

Larger, more powerful models:
- `mistral` - 5GB
- `neural-chat:7b` - 4GB
- `llama3.2` - 7GB

To switch models in Open WebUI:
1. Settings > Models
2. Pull the new model
3. Select it in the chat interface

### Allocate More Resources

Edit `podman-compose.yml` to add resource limits:

```yaml
ollama:
  # ... existing config ...
  cpus: "4"
  memory: "8g"
```

Then restart:
```bash
podman-compose down
podman-compose up -d
```

## Troubleshooting

### "Connection refused" when accessing localhost:3000

```bash
# Check if services are running
podman-compose ps

# If not running, restart
podman-compose down
podman-compose up -d
```

### Slow model loading or inference

```bash
# Check container resource usage
podman stats

# If CPU/Memory maxed, reduce model size or allocate more resources
```

### AI can't access files

```bash
# Check file permissions
ls -la ~/podman-operator/synix_root/

# Make sure files are readable by podman
chmod -R 755 ~/podman-operator/synix_root/
```

### Model download failed

```bash
# Check internet connection
ping 8.8.8.8

# Retry model pull from Open WebUI interface
```

## Advanced: Enable Web Access for AI

To allow the AI to search the web for documentation:

1. Get a free Google Search API key from: https://developers.google.com/custom-search
2. Edit `podman-compose.yml` and add to `open-webui` environment:
   ```yaml
   - GOOGLE_API_KEY=your-key-here
   - GOOGLE_SEARCH_ENGINE_ID=your-engine-id-here
   ```
3. Restart: `podman-compose down && podman-compose up -d`
4. In Open WebUI, enable web search in Settings > Tools

## Next Steps

1. ✅ Deploy Podman + Ollama + Open WebUI
2. ✅ Pull a language model
3. ✅ Test the AI with simple prompts
4. ✅ Grant access to synix_root files
5. ✅ Run your first autonomous task (code review, refactoring, etc.)
6. ✅ Integrate with your Discord bot updates
7. ✅ Set up automated testing of AI-generated code

---

**Documentation Version**: 1.0  
**Last Updated**: 2026-06-23  
**Compatible with**: Podman 4.x, Podman-Compose 1.x
