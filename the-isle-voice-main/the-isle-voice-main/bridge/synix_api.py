import os
import sqlite3
import urllib.parse
import time
from fastapi import FastAPI, Request, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sinisters-map.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STEAM_API_KEY = os.environ.get("STEAM_API_KEY", "")
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "https://sinisters-map.vercel.app"
DB_PATH = "C:/sqlite/synix_rp_backend.db"

# Fixed spawn zones calibrated to Gateway coordinate logic rules
SPAWN_POINTS = {
    "north_plains": {"x": -1200.0, "y": 2500.0},
    "swamp_sanctuary": {"x": 3100.0, "y": -1500.0},
    "center_river": {"x": 0.0, "y": 150.0}
}

class TeleportRequest(BaseModel):
    viewer_steam_id: str
    destination: str

@app.get("/login")
def steam_login():
    steam_openid_url = "https://steamcommunity.com/openid/login"
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": f"{BACKEND_URL}/authorize",
        "openid.realm": BACKEND_URL,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select"
    }
    return RedirectResponse(f"{steam_openid_url}?{urllib.parse.urlencode(params)}")

@app.get("/authorize")
def steam_authorize(request: Request):
    params = dict(request.query_params)
    check_params = params.copy()
    check_params["openid.mode"] = "check_authentication"
    response = requests.post("https://steamcommunity.com/openid/login", data=check_params)
    
    if "is_valid:true" in response.text:
        claimed_id = params.get("openid.claimed_id", "")
        steam_id = claimed_id.split("/")[-1]
        return RedirectResponse(f"{FRONTEND_URL}?steamid={steam_id}")
    
    return {"error": "Steam authentication failed."}

@app.get("/api/map-data")
def get_filtered_map_data(viewer_steam_id: str = Query(...)):
    """
    Handles live radar coordinate array output alongside automated
    eligibility checks for the safe zone countdown rules.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Fetch requesting player's state metrics
        cursor.execute(
            "SELECT role, group_id, species, growth, marks, spawn_timestamp FROM players_slots WHERE steam_id = ?", 
            (viewer_steam_id,)
        )
        viewer = cursor.fetchone()
        
        if not viewer:
            conn.close()
            return {"error": "Unauthorized Viewer Token. Footprint row matching this ID missing."}
            
        role = viewer["role"]
        group_id = viewer["group_id"]
        
        # 2. EVALUATE METRIC CONSTRAINTS: Under 30% Growth & Under 9m 45s (585 seconds)
        current_time = int(time.time())
        spawn_time = viewer["spawn_timestamp"] if viewer["spawn_timestamp"] else current_time
        dino_age_seconds = current_time - spawn_time
        growth_ratio = viewer["growth"] if viewer["growth"] is not None else 0.0
        
        can_teleport = False
        if growth_ratio < 0.30 and dino_age_seconds < 585:
            can_teleport = True

        # 3. Pull spatial telemetry depending on Admin standing
        if role == "Admin":
            cursor.execute("SELECT steam_id, species, marks, pos_x, pos_y, group_id FROM players_slots")
        else:
            if group_id is not None and str(group_id).strip() != "":
                cursor.execute(
                    "SELECT steam_id, species, marks, pos_x, pos_y, group_id FROM players_slots WHERE steam_id = ? OR group_id = ?",
                    (viewer_steam_id, group_id)
                )
            else:
                cursor.execute("SELECT steam_id, species, marks, pos_x, pos_y, group_id FROM players_slots WHERE steam_id = ?", (viewer_steam_id,))
                
        rows = cursor.fetchall()
        conn.close()
        
        player_list = []
        for row in rows:
            player_list.append({
                "steam_id": row["steam_id"],
                "species": row["species"],
                "marks": row["marks"],
                "x": row["pos_x"],
                "y": row["pos_y"],
                "group_id": row["group_id"]
            })
            
        return {
            "viewer_role": role,
            "viewer_species": viewer["species"],
            "viewer_growth": growth_ratio,
            "viewer_marks": viewer["marks"],
            "can_teleport": can_teleport,
            "players": player_list
        }

    except Exception as e:
        return {"error": f"Database interaction drop: {str(e)}"}

@app.get("/api/teleport")
@app.post("/api/teleport")
def handle_teleport_execution(req: TeleportRequest):
    """Enforces boundaries and relocates player parameters inside SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT growth, spawn_timestamp FROM players_slots WHERE steam_id = ?", (req.viewer_steam_id,))
        player = cursor.fetchone()
        
        if not player:
            conn.close()
            return {"error": "Target entity tracking index record not identified."}
            
        current_time = int(time.time())
        spawn_time = player["spawn_timestamp"] if player["spawn_timestamp"] else current_time
        dino_age_seconds = current_time - spawn_time
        growth_ratio = player["growth"] if player["growth"] is not None else 0.0
        
        # Enforce validation rules strictly at execution level to block manipulation
        if growth_ratio >= 0.30:
            conn.close()
            return {"error": f"Warp Rejected: Growth exceeds limits (Current: {int(growth_ratio*100)}%)."}
            
        if dino_age_seconds >= 585:
            conn.close()
            minutes = int(dino_age_seconds // 60)
            seconds = int(dino_age_seconds % 60)
            return {"error": f"Warp Rejected: Dino creation age window expired (Current: {minutes}m {seconds}s)."}
            
        # Target coordinate fetch
        target_coords = SPAWN_POINTS.get(req.destination, SPAWN_POINTS["center_river"])
        
        cursor.execute(
            "UPDATE players_slots SET pos_x = ?, pos_y = ? WHERE steam_id = ?",
            (target_coords["x"], target_coords["y"], req.viewer_steam_id)
        )
        conn.commit()
        conn.close()
        
        return {"message": f"Warp complete! Translocated safely to {req.destination.replace('_', ' ').title()}."}
        
    except Exception as e:
        return {"error": f"Internal database write error: {str(e)}"}