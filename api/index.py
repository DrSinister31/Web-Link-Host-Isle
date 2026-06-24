import sqlite3
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Configuration
DB_PATH = "synix_rp_backend.db"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameStats(BaseModel):
    marks: int
    pKills: int
    aiKills: int
    dinoCount: int
    eggCount: int
    migZone: str
    patrolZone: str
    dinoAge: str

@app.post("/api/update_stats")
async def update_stats(stats: GameStats):
    try:
        with open("/tmp/live_stats.json", "w") as f:
            json.dump(stats.dict(), f)
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/get_live_stats")
async def get_live_stats():
    try:
        if os.path.exists("/tmp/live_stats.json"):
            with open("/tmp/live_stats.json", "r") as f:
                return json.load(f)
        return {"error": "No stats yet"}
    except:
        return {"error": "Read error"}

@app.get("/api/leaderboard")
def get_leaderboard():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, kills FROM players ORDER BY kills DESC LIMIT 10")
        data = [{"name": row[0], "kills": row[1]} for row in cursor.fetchall()]
        conn.close()
        return data
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})