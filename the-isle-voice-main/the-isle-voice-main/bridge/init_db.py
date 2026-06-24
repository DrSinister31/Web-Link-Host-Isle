import sqlite3
from pathlib import Path

# Target location based on config.json
DB_PATH = Path("C:/sqlite/synix_rp_backend.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players_slots (
            steam_id TEXT PRIMARY KEY,
            discord_id TEXT,
            species TEXT,
            growth REAL,
            hunger REAL,
            thirst REAL,
            health REAL,
            protein REAL,
            pos_x REAL,
            pos_y REAL,
            is_paused INTEGER DEFAULT 0,
            marks INTEGER DEFAULT 0,
            free_slots_used INTEGER DEFAULT 0,
            total_slots_unlocked INTEGER DEFAULT 2,
            role TEXT DEFAULT 'User',
            group_id TEXT,
            spawn_timestamp INTEGER
        )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS discord_links (discord_id INTEGER PRIMARY KEY, steam_id TEXT UNIQUE, linked_at INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bot_settings (setting_key TEXT PRIMARY KEY, setting_value TEXT)''')
    
    conn.commit()
    conn.close()
    print("✅ Database verified and initialized at C:/sqlite/synix_rp_backend.db")

if __name__ == "__main__":
    init_db()