"""Configuration data models."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class OverlayConfig:
    """Overlay display configuration."""
    font_family: str = "Segoe UI"
    font_size: int = 14
    color: str = "#00FF00"
    position: str = "top-left"  # top-left, top-right, bottom-left, bottom-right, center
    opacity: float = 0.8
    hotkey: str = "F12"
    show_fps: bool = True
    show_cpu: bool = True
    show_gpu: bool = True
    show_ram: bool = True
    show_temps: bool = True
    
    VALID_POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
    
    def is_valid(self) -> bool:
        """Validate overlay configuration."""
        return (
            self.font_size > 0 and
            self.position in self.VALID_POSITIONS and
            0.0 <= self.opacity <= 1.0 and
            len(self.color) == 7 and self.color.startswith("#")
        )


@dataclass
class FilterConfig:
    """Visual filter configuration for a specific game/program."""
    vibrance: float = 0.0  # 0-100%
    sharpening: float = 0.0  # 0-100%
    brightness: float = 0.0  # -50 to +50%
    contrast: float = 0.0  # -50 to +50%
    enabled: bool = False
    
    def is_valid(self) -> bool:
        """Validate filter configuration."""
        return (
            0.0 <= self.vibrance <= 100.0 and
            0.0 <= self.sharpening <= 100.0 and
            -50.0 <= self.brightness <= 50.0 and
            -50.0 <= self.contrast <= 50.0
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "vibrance": self.vibrance,
            "sharpening": self.sharpening,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "enabled": self.enabled
        }
    
    @staticmethod
    def from_dict(data: dict) -> "FilterConfig":
        """Create from dictionary."""
        return FilterConfig(
            vibrance=data.get("vibrance", 0.0),
            sharpening=data.get("sharpening", 0.0),
            brightness=data.get("brightness", 0.0),
            contrast=data.get("contrast", 0.0),
            enabled=data.get("enabled", False)
        )


@dataclass
class GameFilterProfile:
    """Filter profile for a specific game/program."""
    game_name: str  # Process name or game title
    process_name: str  # Executable name (e.g., "game.exe")
    filters: FilterConfig = field(default_factory=FilterConfig)
    last_used: str = ""  # ISO timestamp
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "game_name": self.game_name,
            "process_name": self.process_name,
            "filters": self.filters.to_dict(),
            "last_used": self.last_used
        }
    
    @staticmethod
    def from_dict(data: dict) -> "GameFilterProfile":
        """Create from dictionary."""
        return GameFilterProfile(
            game_name=data.get("game_name", ""),
            process_name=data.get("process_name", ""),
            filters=FilterConfig.from_dict(data.get("filters", {})),
            last_used=data.get("last_used", "")
        )


@dataclass
class OptimizerConfig:
    """Game optimization configuration."""
    processes_to_terminate: List[str] = field(default_factory=lambda: [
        "OneDrive.exe", "Cortana.exe", "SearchUI.exe"
    ])
    set_high_priority: bool = True
    clear_ram: bool = True
    set_timer_resolution: bool = True
    timer_resolution_ms: float = 0.5


@dataclass
class LicenseConfig:
    """License information."""
    license_key: str = ""
    is_activated: bool = False
    username: str = ""
    expiry_date: str = ""


@dataclass
class Theme:
    """UI theme configuration."""
    name: str = "default"
    colors: dict = field(default_factory=dict)
    font_family: str = "Segoe UI"
    font_size: int = 14
    background_color: str = "#1e1e1e"
    opacity: float = 0.8
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "colors": self.colors,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "background_color": self.background_color,
            "opacity": self.opacity
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Theme":
        """Create from dictionary."""
        return Theme(
            name=data.get("name", "default"),
            colors=data.get("colors", {}),
            font_family=data.get("font_family", "Segoe UI"),
            font_size=data.get("font_size", 14),
            background_color=data.get("background_color", "#1e1e1e"),
            opacity=data.get("opacity", 0.8)
        )


@dataclass
class AppConfig:
    """Main application configuration."""
    auto_start: bool = False
    minimize_to_tray: bool = True
    logging_enabled: bool = False
    show_temp_warning: bool = True  # Show temperature monitoring warning on first run
    skipped_version: str = ""  # Version user chose to skip
    overlay: OverlayConfig = field(default_factory=OverlayConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    license: LicenseConfig = field(default_factory=LicenseConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)  # Default filters
    game_filter_profiles: dict = field(default_factory=dict)  # game_name -> GameFilterProfile
    themes: dict = field(default_factory=dict)  # theme_name -> Theme
    hotkeys: dict = field(default_factory=lambda: {
        "toggle_overlay": "F12",
        "toggle_game_mode": "F11",
        "start_benchmark": "F10"
    })
    
    def get_default() -> "AppConfig":
        """Return default configuration."""
        return AppConfig()
