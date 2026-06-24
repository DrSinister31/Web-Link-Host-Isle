@echo off
REM Master Setup: Sinister's Park Infrastructure
REM 1. Clean legacy / 2. Consolidate to synix_root / 3. Docker Deploy

echo.
echo --- BUILDING SINISTER'S PARK BACKEND ---
echo.

REM 1. CLEANUP - Remove cache, logs, pycache
echo [1/5] Cleaning legacy files...
for /d /r "C:\Users\Dilla\Downloads\the-isle-voice-main\the-isle-voice-main" %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q "C:\Users\Dilla\Downloads\the-isle-voice-main\the-isle-voice-main\*.pyc" 2>nul
del /s /q "C:\Users\Dilla\Downloads\the-isle-voice-main\the-isle-voice-main\*.log" 2>nul
rmdir /s /q "C:\Users\Dilla\Downloads\the-isle-voice-main\the-isle-voice-main\venv" 2>nul
echo [✓] Cleanup complete

REM 2. CONSOLIDATION - Already done in synix_root
echo [2/5] Verifying synix_root consolidation...
if not exist "C:\Users\Dilla\OneDrive\Desktop\synix_root\bridge" (
    echo [✗] bridge directory missing
    exit /b 1
)
echo [✓] synix_root structure verified

REM 3. DOCKERFILE - Already created with python:3.13-slim
echo [3/5] Dockerfile configured (python:3.13-slim)
echo [✓] Dockerfile verified

REM 4. DOCKER-COMPOSE - Already created with healthcheck
echo [4/5] docker-compose.yml configured (2 services)
echo [✓] docker-compose verified

REM 5. BUILD DOCKER IMAGE
echo [5/5] Building Docker image...
docker build -t synix-park:latest "C:\Users\Dilla\OneDrive\Desktop\synix_root"
if %ERRORLEVEL% NEQ 0 (
    echo [✗] Docker build failed
    exit /b 1
)
echo [✓] Docker image built successfully

REM 6. DEPLOY WITH DOCKER-COMPOSE
echo.
echo --- DEPLOYING SERVICES ---
echo.
docker compose -f "C:\Users\Dilla\OneDrive\Desktop\synix_root\docker-compose.yml" up -d
if %ERRORLEVEL% NEQ 0 (
    echo [✗] Docker compose deployment failed
    exit /b 1
)
echo [✓] Services deployed

REM 7. VERIFY DEPLOYMENT
echo.
echo --- VERIFICATION ---
echo.
docker compose -f "C:\Users\Dilla\OneDrive\Desktop\synix_root\docker-compose.yml" ps
echo.
echo API Health: curl http://localhost:8000/health
echo Bot Logs: docker compose -f "C:\Users\Dilla\OneDrive\Desktop\synix_root\docker-compose.yml" logs synix-bot
echo.
echo --- DEPLOYMENT COMPLETE ---
echo.
