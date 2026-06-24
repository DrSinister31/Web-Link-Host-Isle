import sys
import os
from pathlib import Path

# Add the current root directory to sys.path
sys.path.append(str(Path(__file__).parent.resolve()))

# Now import and run the bot from the bridge folder
from bridge.synix_bot_3 import bot

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("ERROR: DISCORD_TOKEN environment variable not set")
        sys.exit(1)
    bot.run(token)
