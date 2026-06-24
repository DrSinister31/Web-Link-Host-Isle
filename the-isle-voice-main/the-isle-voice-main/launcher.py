import sys
from pathlib import Path

# Add the current root directory to sys.path
sys.path.append(str(Path(__file__).parent.resolve()))

# Now import and run the bot from the bridge folder
import bridge.synix_bot_3