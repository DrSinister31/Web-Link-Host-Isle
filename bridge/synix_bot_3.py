import sqlite3
import discord
import requests
from bridge.rcon_bridge import send_rcon, is_admin

# Path to your database
DB_PATH = "synix_rp_backend.db"

def get_steam_id(discord_id):
    """Helper to retrieve Steam ID from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT steam_id FROM discord_links WHERE discord_id = ?", (discord_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

async def execute_rcon_command(interaction, cmd, steam_id):
    """Helper to execute RCON and notify the dashboard."""
    response = send_rcon(f"{cmd} {steam_id}")
    await interaction.response.send_message(f"✅ {response}")
    
    # Notify dashboard of the status change
    try:
        requests.post("https://sinister-tracker.vercel.app/api/update_stats", 
                      json={"action": cmd, "steam_id": steam_id})
    except Exception as e:
        print(f"Dashboard sync error: {e}")

@bot.tree.command(name="pause", description="Pause your saved dino")
async def pause_cmd(interaction: discord.Interaction):
    steam_id = get_steam_id(interaction.user.id)
    if not steam_id:
        await interaction.response.send_message("❌ Link your Steam ID first with `/link`", ephemeral=True)
        return
    await execute_rcon_command(interaction, "AdminPause", steam_id)

@bot.tree.command(name="unpause", description="Unpause your dino")
async def unpause_cmd(interaction: discord.Interaction):
    steam_id = get_steam_id(interaction.user.id)
    if not steam_id:
        await interaction.response.send_message("❌ Link your Steam ID first with `/link`", ephemeral=True)
        return
    await execute_rcon_command(interaction, "AdminUnpause", steam_id)