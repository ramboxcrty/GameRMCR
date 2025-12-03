"""Game detection for automatic overlay activation."""
import psutil
from typing import List, Optional, Set


class GameDetector:
    """Detect running games for automatic overlay activation."""
    
    # Common game executables
    KNOWN_GAMES = {
        # Popular games
        "csgo.exe", "cs2.exe", "valorant.exe", "fortnite.exe",
        "gta5.exe", "gtav.exe", "rdr2.exe",
        "minecraft.exe", "javaw.exe",  # Minecraft Java
        "dota2.exe", "leagueoflegends.exe", "lol.exe",
        "overwatch.exe", "apex_legends.exe",
        "pubg.exe", "tslgame.exe",
        "cyberpunk2077.exe", "eldenring.exe",
        "witcher3.exe", "rocketleague.exe",
        # Launchers that might indicate gaming
        "steam.exe", "epicgameslauncher.exe", "origin.exe",
    }
    
    def __init__(self, custom_games: Optional[List[str]] = None):
        self.custom_games: Set[str] = set(custom_games or [])
        self._detected_game: Optional[str] = None
        self._detected_pid: Optional[int] = None
    
    def add_custom_game(self, exe_name: str) -> None:
        """Add a custom game executable to detect."""
        self.custom_games.add(exe_name.lower())
    
    def remove_custom_game(self, exe_name: str) -> None:
        """Remove a custom game from detection."""
        self.custom_games.discard(exe_name.lower())
    
    def detect_game(self) -> Optional[tuple[str, int]]:
        """Detect if a game is running.
        
        Returns:
            Tuple of (game_name, pid) if found, None otherwise
        """
        all_games = self.KNOWN_GAMES | self.custom_games
        
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                name = proc.info['name'].lower()
                if name in all_games:
                    self._detected_game = name
                    self._detected_pid = proc.info['pid']
                    return (name, proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self._detected_game = None
        self._detected_pid = None
        return None
    
    def is_game_running(self) -> bool:
        """Check if any game is currently running."""
        return self.detect_game() is not None
    
    @property
    def current_game(self) -> Optional[str]:
        """Get the currently detected game name."""
        return self._detected_game
    
    @property
    def current_game_pid(self) -> Optional[int]:
        """Get the PID of the currently detected game."""
        return self._detected_pid
