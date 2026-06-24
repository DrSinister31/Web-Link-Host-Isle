import os
import sqlite3
from mcrcon import MCRcon

ADMIN_LIST_PATH = "/app/data/game.ini"
DB_FILE = os.getenv("DB_PATH", "/app/data/synix_rp_backend.db")

def get_admin_list():
    try:
        with open(ADMIN_LIST_PATH, 'r') as f:
            return [line.strip().split('=')[1] for line in f if "Steam64ID=" in line]
    except:
        return []

def is_admin(steam_id):
    return str(steam_id) in get_admin_list()

def check_saved_status(steam_id):
    """Check if the player has saved their dino in the DB."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT saved_status FROM players_slots WHERE steam_id = ?", (str(steam_id),))
        row = cursor.fetchone()
        conn.close()
        return row[0] == 1 if row else False
    except:
        return False

def send_rcon(command):
    try:
        with MCRcon(os.getenv("RCON_HOST"), os.getenv("RCON_PASSWORD"), port=int(os.getenv("RCON_PORT", 8888))) as mcr:
            return mcr.command(command)
    except Exception as e:
        return f"Error: {e}"