import sys
from pathlib import Path

# Force the root directory into the path before anything else
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import discord
from discord import app_commands
import sqlite3
import time

# Now the import should succeed
from config import AppConfig

# Config load
config_path = root_dir / "config.json"
app_config = AppConfig.load(config_path)
db_file_path = app_config.path_value("database.path", "C:/sqlite/synix_rp_backend.db")

class SynixBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"🤖 SINISTER'S PARK | {self.user}")
        await self.tree.sync()

bot = SynixBot()

@bot.tree.command(name="link", description="Bind Steam ID to Discord.")
async def link_account(interaction: discord.Interaction, steam_id: str):
    conn = sqlite3.connect(str(db_file_path))
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO discord_links (discord_id, steam_id, linked_at) VALUES (?, ?, ?)", 
                   (interaction.user.id, steam_id, int(time.time())))
    conn.commit()
    conn.close()
    await interaction.response.send_message("✅ Account linked!", ephemeral=True)

if __name__ == "__main__":
    # Ensure you use your valid token here
    bot.run("YOUR_TOKEN_HERE")