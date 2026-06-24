# Synix Park Deployment Checklist

## ✅ Setup Complete

### Project Structure
- [x] Dockerfile (python:3.13-slim, multi-stage optimized)
- [x] docker-compose.yml (2 services: API + Bot)
- [x] requirements.txt (all dependencies pinned)
- [x] .dockerignore (excludes cache, venv, logs)
- [x] .env (secrets template with placeholder values)
- [x] .env.example (shareable template)

### Source Code
- [x] launcher.py (bot entry point)
- [x] bridge/synix_api.py (FastAPI + Steam OAuth + Teleportation)
- [x] bridge/synix_bot_3.py (Discord bot with account linking)
- [x] bridge/config.py (config loader)

### CI/CD
- [x] .github/workflows/docker-build-push.yml (GitHub Actions)
  - Auto-builds on push to main
  - Pushes to Docker Hub with tags (latest + git SHA)
  - Layer caching enabled for speed

### Documentation
- [x] README.md (setup guide, endpoints, troubleshooting)
- [x] deploy.sh (bash deployment script)

### Verification
- [x] Docker image builds successfully (350MB, python:3.13-slim)
- [x] docker-compose config validates correctly
- [x] Both services defined with healthcheck (API)
- [x] Database volume mapped to ./data/
- [x] RCON environment variables configured

---

## 🚀 Next Steps

### Before Deployment

1. **Fill in .env secrets**:
   ```bash
   DISCORD_TOKEN=your_bot_token
   STEAM_API_KEY=your_api_key
   RCON_HOST=172.93.104.174
   RCON_PORT=2463
   ```

2. **Migrate database** (if needed):
   ```bash
   # Copy synix_rp_backend.db to ./data/
   cp C:/sqlite/synix_rp_backend.db ./data/
   ```

3. **Create data directory**:
   ```bash
   mkdir -p data
   ```

### Deploy Locally

```bash
docker compose up -d
```

### Deploy to Production

**Option A: Docker Hub Push via GitHub**
1. Create Docker Hub account (docker.io)
2. Add GitHub Secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
3. Push to main branch → automatic build + push to `username/synix-park:latest`

**Option B: Manual Push**
```bash
docker login -u <username>
docker tag synix-park:latest <username>/synix-park:latest
docker push <username>/synix-park:latest
```

**Option C: Docker Compose on Swarm**
```bash
docker swarm init
docker stack deploy -c docker-compose.yml synix
```

---

## 📊 Service Architecture

```
┌─────────────────────────────────────┐
│      Docker Compose Network         │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │   synix-api (FastAPI)        │  │
│  │   Port: 8000                 │  │
│  │   Health: /health            │  │
│  │   Endpoints:                 │  │
│  │   - /login (Steam OAuth)     │  │
│  │   - /authorize               │  │
│  │   - /api/map-data            │  │
│  │   - /api/teleport            │  │
│  └──────────────────────────────┘  │
│            ↓ (depends_on healthy)   │
│  ┌──────────────────────────────┐  │
│  │   synix-bot (Discord)        │  │
│  │   Commands:                  │  │
│  │   - /link (account linking)  │  │
│  │   - RCON bridge              │  │
│  │   - Database integration     │  │
│  └──────────────────────────────┘  │
│            ↓ (both share)            │
│  ┌──────────────────────────────┐  │
│  │   Volumes:                   │  │
│  │   - ./data/ (SQLite DB)      │  │
│  │   - ./bridge/ (bot code)     │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔐 Security Reminders

- [ ] Never commit .env to Git (use .gitignore)
- [ ] Rotate DISCORD_TOKEN and STEAM_API_KEY regularly
- [ ] Use strong RCON password for production
- [ ] Enable CORS restrictions in synix_api.py
- [ ] Back up ./data/synix_rp_backend.db regularly
- [ ] Run containers as non-root in production

---

## 📈 Scaling Notes

- **Single Host**: docker-compose works fine for dev/small prod
- **Multi-Host**: Use Docker Swarm or Kubernetes
- **Database**: SQLite suitable for < 100 concurrent users
  - For scaling: migrate to PostgreSQL
  - Update DB_PATH to postgres://user:pass@host/db

---

## ✅ Deployment Verification Commands

```bash
# Check services running
docker compose ps

# Verify API health
curl http://localhost:8000/health

# Check bot logs
docker compose logs synix-bot -f

# Inspect network
docker network inspect synix_root_default

# View image size
docker images | grep synix-park

# Test database access (inside container)
docker compose exec synix-api sqlite3 /app/data/synix_rp_backend.db ".tables"
```

---

**Status**: ✅ Ready for Deployment
**Image Size**: ~350MB
**Services**: 2 (API + Bot)
**Database**: SQLite (persistent volume)
**CI/CD**: GitHub Actions configured
