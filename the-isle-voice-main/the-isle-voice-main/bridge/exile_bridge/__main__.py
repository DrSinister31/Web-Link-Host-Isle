from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Importing components from your project structure
from .bridge import Bridge, probe_rcon
from .config import AppConfig
from .parser import parse_players

def main() -> int:
    """
    Clean entry point for the local bridge process.
    Run this inside your Docker container ONLY.
    """
    parser = argparse.ArgumentParser(prog="exile_bridge")
    sub = parser.add_subparsers(dest="command", required=True)

    # Command: Run the actual persistent socket bridge
    run_p = sub.add_parser("run", help="Run the proximity bridge")
    run_p.add_argument("--config", required=True)
    run_p.add_argument("--once", action="store_true")

    # Command: Parse logic for local debugging
    parse_p = sub.add_parser("parse", help="Parse player data")
    parse_p.add_argument("--file", required=True)

    # Command: RCON Probing
    probe_p = sub.add_parser("probe-rcon", help="Probe RCON commands")
    probe_p.add_argument("--config", required=True)

    args = parser.parse_args()

    # --- Execution Logic ---
    if args.command == "run":
        print("Starting persistent bridge...")
        config = AppConfig.load(args.config)
        Bridge(config).run(once=args.once)
        return 0

    if args.command == "parse":
        text = Path(args.file).read_text(encoding="utf-8")
        players = parse_players(text)
        for player in players:
            pos = f"X={player.position.x:.1f} Y={player.position.y:.1f}" if player.position else "no-position"
            print(f"{player.display_name} | {pos}")
        return 0

    if args.command == "probe-rcon":
        config = AppConfig.load(args.config)
        out_path = probe_rcon(config)
        print(f"Transcript saved to: {out_path}")
        return 0

    return 1

if __name__ == "__main__":
    # Use standard sys.exit for cleaner docker process termination
    sys.exit(main())