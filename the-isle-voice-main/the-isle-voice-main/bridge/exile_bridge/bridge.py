from __future__ import annotations

import time
import socketio
from pathlib import Path

from .config import AppConfig
from .falloff_server import FalloffServer, FalloffSettings
from .identity import IdentityMap
from .models import Player
from .mumble import MumbleAdapter, make_mumble_adapter
from .parser import parse_players
from .proximity import ProximityConfig, ProximityEngine
from .rcon_client import RconSettings, TheIsleRconClient
from .verification import VerificationManager, VerifySettings

class Bridge:
    def __init__(self, config: AppConfig):
        self.config = config
        self.mode = str(config.get("mode", "mock")).lower()
        self.poll_interval = float(config.get("poll_interval_sec", 3.0))
        self.identity_path = config.path_value("identity_map_file", "identity_map.example.json")
        self.identity = IdentityMap.load(self.identity_path)
        self.proximity = ProximityEngine(ProximityConfig.from_dict(config.get("proximity", {})))
        
        mumble_config = config.get("mumble", {})
        self.mumble: MumbleAdapter = make_mumble_adapter(mumble_config, str(mumble_config.get("root_channel", "The Isle - Lobby")))
        self.falloff = FalloffServer(FalloffSettings.from_dict(config.get("falloff_server", {})))
        
        self.verifier = VerificationManager(
            VerifySettings.from_config(config),
            self.identity_path,
            RconSettings.from_dict(config.get("rcon", {})),
            plugin_hashes=self.falloff.connected_hashes,
        )

        # Initialize SocketIO for Frontend Communication
        # Allowing '*' allows your GitHub Pages panel to connect freely
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")

    def run(self, once: bool = False) -> None:
        self.falloff.start()
        self.verifier.start()
        try:
            while True:
                self.tick()
                if once:
                    break
                time.sleep(self.poll_interval)
        finally:
            self.verifier.stop()
            self.falloff.stop()

    def tick(self) -> None:
        players = self.fetch_players()
        self.verifier.update_players(players)
        self.verifier.poll_game_chat()
        self.identity = IdentityMap.load(self.identity_path)
        players = [self.identity.apply(player) for player in players]
        assignments = self.proximity.assign_channels(players)
        matrix = self.proximity.audio_matrix(players)

        self.mumble.sync(players, assignments)
        self.falloff.publish(matrix)

    def fetch_players(self) -> list[Player]:
        if self.mode == "mock":
            fixture = self.config.path_value("mock.fixture", "fixtures/sample_playerdata.txt")
            return parse_players(fixture.read_text(encoding="utf-8"))
        if self.mode == "rcon":
            return self._fetch_players_rcon()
        raise ValueError(f"Unknown mode: {self.mode}")

    def _fetch_players_rcon(self) -> list[Player]:
        settings = RconSettings.from_dict(self.config.get("rcon", {}))
        commands = list(self.config.get("rcon.commands", ["PlayerData"]))
        transcript: list[str] = []
        with TheIsleRconClient(settings) as client:
            for command in commands:
                response = client.command(str(command))
                transcript.append(f"===== {command} =====\n{response}")
        return parse_players("\n".join(transcript))