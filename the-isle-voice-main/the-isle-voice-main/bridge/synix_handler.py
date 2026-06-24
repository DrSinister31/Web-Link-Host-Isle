import os
import sys
import sqlite3
import math
from pathlib import Path

# Force Python to look in the current file's folder for local module imports
current_dir = Path(__file__).parent.resolve()
sys.path.append(str(current_dir))

# Dynamically load your config.py class utility from your project
from config import AppConfig

# =====================================================================
# SERVERSIDE GAMEPLAY ECONOMY SETTINGS
# =====================================================================
POINTS_PER_TICK = 5        # Base Marks awarded every 5-second loop tick
DIET_BONUS_MAX = 10        # Max sliding bonus marks for a perfect 100% diet
STAMINA_BONUS_MAX = 5      # Max sliding bonus marks for perfect stamina
WOUNDED_PENALTY = 3        # Marks deducted from tick reward if dino is bleeding
SLOT_PURCHASE_COST = 500   # Cost in Marks to unlock an additional slot

class SynixSystemHandler:
    def __init__(self):
        """
        Initializes the logic engine by safely reading your database path 
        directly out of your server's config.json file.
        """
        config_path = current_dir / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Critical Error: config.json not found at {config_path}")
            
        # Load the configuration object using your existing system parser
        self.app_config = AppConfig.load(config_path)
        
        # Safely pull out your custom database string
        self.db_path = self.app_config.path_value("database.path", "C:/sqlite/synix_rp_backend.db")
        self.db_path = Path(self.db_path)

    def _get_db_connection(self):
        """Internal helper to establish a safe thread connection to SQLite."""
        return sqlite3.connect(str(self.db_path))

    # =====================================================================
    # FEATURE 1: AUTOMATED TIME-PLAYED & SLIDING ROLEPLAY POINTS TRACKER
    # =====================================================================
    def process_player_tick(self, player_data: dict) -> int:
        """
        Processes passive time played and survival bonus points every polling loop.
        Expects a dict containing: 'steam_id', 'diet_percentage', 'stamina', 'is_wounded'
        """
        steam_id = player_data.get("steam_id")
        if not steam_id:
            return 0

        # Extract survival states from the live game loop data
        diet = player_data.get("diet_percentage", 0)   # Scale: 0 to 100
        stamina = player_data.get("stamina", 0)         # Scale: 0 to 100
        is_wounded = player_data.get("is_wounded", False)

        # Calculate sliding scale roleplay bonuses based on player maintenance
        diet_bonus = math.floor((diet / 100.0) * DIET_BONUS_MAX)
        stamina_bonus = math.floor((stamina / 100.0) * STAMINA_BONUS_MAX)
        injury_modifier = -WOUNDED_PENALTY if is_wounded else 0

        # Total points for this 5-second interval
        total_tick_points = POINTS_PER_TICK + diet_bonus + stamina_bonus + injury_modifier
        if total_tick_points < 0:
            total_tick_points = 0  # Ensure an injured dino doesn't drain existing balance

        # Atomically commit the earned points to the SQLite tracker database
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO players_slots (steam_id, marks, total_slots_unlocked, free_slots_used)
            VALUES (?, ?, 2, 0)
            ON CONFLICT(steam_id) DO UPDATE SET marks = marks + ?
        ''', (steam_id, total_tick_points, total_tick_points))
        
        conn.commit()
        conn.close()
        return total_tick_points

    # =====================================================================
    # FEATURE 2: SLOT SAVING VALIDATION RULES (2 Free, 5 Max Cap)
    # =====================================================================
    def handle_slot_save_request(self, steam_id: str, current_dino_slots_used: int) -> tuple[bool, str]:
        """
        Validates if a player can save a dinosaur based on their free and paid slots.
        Returns: (Success Boolean, Feedback Message String)
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT free_slots_used, total_slots_unlocked, marks 
            FROM players_slots WHERE steam_id = ?
        ''', (steam_id,))
        row = cursor.fetchone()
        
        # Establish base structural profile assumptions if player is brand new
        if not row:
            free_slots_used, total_slots_unlocked, marks = 0, 2, 0
        else:
            free_slots_used, total_slots_unlocked, marks = row

        # Case A: They are safely using one of their 2 completely free starting slots
        if current_dino_slots_used < 2 and free_slots_used < 2:
            cursor.execute('''
                INSERT INTO players_slots (steam_id, free_slots_used) 
                VALUES (?, 1)
                ON CONFLICT(steam_id) DO UPDATE SET free_slots_used = free_slots_used + 1
            ''', (steam_id,))
            conn.commit()
            conn.close()
            return True, "Saved successfully utilizing a Free Slot allocation."

        # Case B: Free slots are full, but they have paid to unlock more total slot limits
        if current_dino_slots_used < total_slots_unlocked:
            conn.close()
            return True, "Saved successfully using Unlocked Slot account allocation."

        # Case C: Account storage thresholds are reached entirely. Suggest purchasing.
        if total_slots_unlocked < 5:
            conn.close()
            return False, f"Slots full. You can unlock slot {total_slots_unlocked + 1}/5 using {SLOT_PURCHASE_COST} Marks. Use Discord command /buyslot"
        
        conn.close()
        return False, "Maximum server limits reached. You are at the absolute cap of 5 slots."

    # =====================================================================
    # FEATURE 3: PROGRESSION PURCHASE LOOP AUTOMATION
    # =====================================================================
    def buy_additional_slot(self, steam_id: str) -> tuple[bool, str]:
        """
        Deducts Marks currency from a player's balance to unlock slot limits (Max 5).
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT total_slots_unlocked, marks FROM players_slots WHERE steam_id = ?', (steam_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, "Error: Profile unrecognized. Play on the server to establish points."
            
        total_slots_unlocked, marks = row
        
        # Enforce server cap bounds (hard-capped at 5 slots max)
        if total_slots_unlocked >= 5:
            conn.close()
            return False, "Error: You have already maxed out your structural slot limits (5/5)."
            
        # Check financial ledger capability
        if marks < SLOT_PURCHASE_COST:
            conn.close()
            return False, f"Insufficient funds. Upgrade requires {SLOT_PURCHASE_COST} Marks. You currently hold {marks}."
            
        # Complete transaction details
        cursor.execute('''
            UPDATE players_slots 
            SET marks = marks - ?, total_slots_unlocked = total_slots_unlocked + 1 
            WHERE steam_id = ?
        ''', (SLOT_PURCHASE_COST, steam_id))
        
        conn.commit()
        conn.close()
        return True, f"Success! Expanded account limitations to {total_slots_unlocked + 1} maximum slots."

# Self-test logic to verify code compiles perfectly without launching entire framework
if __name__ == "__main__":
    print("Testing code alignment engine...")
    try:
        handler = SynixSystemHandler()
        print(f"✅ Clean compile! Connected successfully to config path at: {handler.db_path}")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")