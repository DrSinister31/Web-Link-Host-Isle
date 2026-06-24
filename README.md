# Synix Park - Docker Deployment

Complete Docker setup for Sinister's Park infrastructure with Discord bot, FastAPI server, and RCON bridge.

## Features

- **Discord Bot** (synix-bot): Command-driven player management and database integration
- **FastAPI Server** (synix-api): Steam OAuth, player tracking, teleportation API
- **Database**: SQLite with persistent volume mounting
- **RCON Integration**: Server command execution via Minecraft RCON protocol
- **Health Checks**: Automatic service liveness monitoring
- **CI/CD**: GitHub Actions auto-build and push to Docker Hub

## Quick Start

### 1. Configure Secrets

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DISCORD_TOKEN=your_bot_token_here
STEAM_API_KEY=your_api_key_here
RCON_HOST=172.93.104.174
RCON_PORT=2463
```

### 2. Create Data Directory

```bash
mkdir -p data
```

### 3. Start Services

```bash
docker compose up
```

Or in detached mode:

```bash
docker compose up -d
```

### 4. Verify Services

- **API Health**: `curl http://localhost:8000/health`
- **Bot Logs**: `docker compose logs synix-bot`
- **API Logs**: `docker compose logs synix-api`

## Project Structure

```
synix_root/
├── Dockerfile              # Multi-stage Python 3.13-slim image
├── docker-compose.yml      # Two-service orchestration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (secrets)
├── .env.example            # Template for .env
├── .dockerignore           # Build context exclusions
├── launcher.py             # Bot entry point
├── bridge/
│   ├── synix_api.py       # FastAPI endpoints
│   ├── synix_bot_3.py     # Discord bot commands
│   ├── config.py          # Config loader
│   └── synix_handler.py   # RCON handler (optional)
├── data/                   # Persistent SQLite database
└── .github/workflows/
    └── docker-build-push.yml  # CI/CD pipeline
```

## API Endpoints

- `GET /health` - Service health check
- `GET /login` - Steam OAuth redirect
- `GET /authorize` - Steam callback handler
- `GET /api/map-data?viewer_steam_id=<id>` - Fetch player positions
- `POST /api/teleport` - Execute player teleportation

## Environment Variables

| Variable | Default | Required |
|----------|---------|----------|
| `DISCORD_TOKEN` | N/A | ✅ Yes |
| `STEAM_API_KEY` | N/A | ✅ Yes |
| `RCON_HOST` | 172.93.104.174 | ✅ Yes |
| `RCON_PORT` | 2463 | ✅ Yes |
| `DB_PATH` | /app/data/synix_rp_backend.db | No |
| `BACKEND_URL` | http://localhost:8000 | No |
| `FRONTEND_URL` | https://sinisters-map.vercel.app | No |

## CI/CD Setup

### GitHub Actions

To auto-build and push to Docker Hub:

1. **Create Docker Hub Account** (if not already done)
2. **Add GitHub Secrets**:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub access token (not password)
3. **Push to main branch** → Automatic build and push to `<username>/synix-park:latest`

The workflow builds multi-arch images using Buildx and caches layers for faster rebuilds.

## Database Schema

Ensure your SQLite database has these tables:

```sql
CREATE TABLE IF NOT EXISTS players_slots (
    steam_id TEXT PRIMARY KEY,
    discord_id TEXT,
    role TEXT DEFAULT 'Player',
    group_id TEXT,
    species TEXT,
    growth REAL,
    marks INTEGER,
    pos_x REAL,
    pos_y REAL,
    spawn_timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS discord_links (
    discord_id INTEGER PRIMARY KEY,
    steam_id TEXT UNIQUE,
    linked_at INTEGER
);
```

## Troubleshooting

### Bot not starting
```bash
docker compose logs synix-bot
# Check DISCORD_TOKEN in .env
```

### API returning 500 errors
```bash
docker compose logs synix-api
# Verify DB_PATH and database file exists in ./data/
```

### Health check failing
```bash
docker compose ps
docker inspect synix_root-synix-api-1
# Check if service is listening on port 8000
```

### Database locked
```bash
# Ensure only one container writes to SQLite at a time
# Or migrate to PostgreSQL for concurrent access
```

## Deployment Options

### Local Development
```bash
docker compose up
```

### Production (Docker Swarm)
```bash
docker stack deploy -c docker-compose.yml synix
```

### Production (Kubernetes)
See `k8s/` directory for manifests.

### Cloud (AWS, GCP, Azure)
1. Push image to ECR/GAR/ACR
2. Deploy via ECS/Cloud Run/Container Instances
3. Set environment variables via cloud console

## Performance Notes

- **Image Size**: ~350MB (python:3.13-slim + dependencies)
- **Memory**: ~256MB per service (API + Bot)
- **Database**: Single SQLite file; consider PostgreSQL for scaling
- **Network**: Both services share a Docker bridge network

## Security

- **Secrets**: Use `.env` and never commit to Git
- **Database**: Mount as volume; back up `data/synix_rp_backend.db` regularly
- **CORS**: API restricts origins to `https://sinisters-map.vercel.app`
- **Non-root**: Consider running containers as non-root user

## Support

For issues, check:
- Docker logs: `docker compose logs`
- Health endpoint: `curl http://localhost:8000/health`
- Network: `docker network ls && docker network inspect synix_root_default`
