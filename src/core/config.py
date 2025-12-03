"""Configuration Manager for GamePP Clone."""
import json
from pathlib import Path
from dataclasses import asdict, fields
from typing import List, Optional, Any
from src.models.config import AppConfig, OverlayConfig, OptimizerConfig, LicenseConfig


class ConfigManager:
    """Manages application configuration with load/save functionality."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: AppConfig = AppConfig()
        self._default_config = AppConfig()
    
    def load(self) -> AppConfig:
        """Load configuration from file."""
        if not self.config_path.exists():
            self.config = AppConfig()
            return self.config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.config = self._dict_to_config(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupted file - reset to defaults
            self.reset_to_defaults()
        
        return self.config
    
    def save(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = self._config_to_dict(self.config)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to factory defaults."""
        self.config = AppConfig()
        self.save()
    
    def validate(self) -> List[str]:
        """Validate current configuration. Returns list of errors."""
        errors = []
        
        # Validate overlay config
        if self.config.overlay.font_size <= 0:
            errors.append("Font size must be positive")
        if self.config.overlay.position not in OverlayConfig.VALID_POSITIONS:
            errors.append(f"Invalid position: {self.config.overlay.position}")
        if not (0.0 <= self.config.overlay.opacity <= 1.0):
            errors.append("Opacity must be between 0 and 1")
        if not self._is_valid_color(self.config.overlay.color):
            errors.append(f"Invalid color format: {self.config.overlay.color}")
        if not self.config.overlay.font_family:
            errors.append("Font family cannot be empty")
        
        # Validate optimizer config
        if self.config.optimizer.timer_resolution_ms <= 0:
            errors.append("Timer resolution must be positive")
        if self.config.optimizer.timer_resolution_ms > 15.6:
            errors.append("Timer resolution cannot exceed 15.6ms")
        
        # Validate hotkeys
        hotkey_values = list(self.config.hotkeys.values())
        if self.config.overlay.hotkey:
            hotkey_values.append(self.config.overlay.hotkey)
        if len(hotkey_values) != len(set(hotkey_values)):
            errors.append("Duplicate hotkey assignments detected")
        
        return errors
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color is valid hex format."""
        if not color or len(color) != 7 or not color.startswith("#"):
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def is_valid(self) -> bool:
        """Check if current configuration is valid."""
        return len(self.validate()) == 0

    
    def save_license(self, license_key: str, username: str = "", expiry_date: str = "") -> None:
        """Save license information to config."""
        self.config.license.license_key = license_key
        self.config.license.is_activated = True
        self.config.license.username = username
        self.config.license.expiry_date = expiry_date
        self.save()
    
    def get_license(self) -> LicenseConfig:
        """Get license information from config."""
        return self.config.license
    
    def is_license_activated(self) -> bool:
        """Check if license is activated."""
        return self.config.license.is_activated and bool(self.config.license.license_key)
    
    def _config_to_dict(self, config: AppConfig) -> dict:
        """Convert AppConfig to dictionary for JSON serialization."""
        return {
            "auto_start": config.auto_start,
            "minimize_to_tray": config.minimize_to_tray,
            "logging_enabled": config.logging_enabled,
            "overlay": {
                "font_family": config.overlay.font_family,
                "font_size": config.overlay.font_size,
                "color": config.overlay.color,
                "position": config.overlay.position,
                "opacity": config.overlay.opacity,
                "hotkey": config.overlay.hotkey,
                "show_fps": config.overlay.show_fps,
                "show_cpu": config.overlay.show_cpu,
                "show_gpu": config.overlay.show_gpu,
                "show_ram": config.overlay.show_ram,
                "show_temps": config.overlay.show_temps,
            },
            "optimizer": {
                "processes_to_terminate": config.optimizer.processes_to_terminate,
                "set_high_priority": config.optimizer.set_high_priority,
                "clear_ram": config.optimizer.clear_ram,
                "set_timer_resolution": config.optimizer.set_timer_resolution,
                "timer_resolution_ms": config.optimizer.timer_resolution_ms,
            },
            "license": {
                "license_key": config.license.license_key,
                "is_activated": config.license.is_activated,
                "username": config.license.username,
                "expiry_date": config.license.expiry_date,
            },
            "hotkeys": config.hotkeys,
        }
    
    def _dict_to_config(self, data: dict) -> AppConfig:
        """Convert dictionary to AppConfig."""
        overlay_data = data.get("overlay", {})
        optimizer_data = data.get("optimizer", {})
        license_data = data.get("license", {})
        
        overlay = OverlayConfig(
            font_family=overlay_data.get("font_family", "Segoe UI"),
            font_size=overlay_data.get("font_size", 14),
            color=overlay_data.get("color", "#00FF00"),
            position=overlay_data.get("position", "top-left"),
            opacity=overlay_data.get("opacity", 0.8),
            hotkey=overlay_data.get("hotkey", "F12"),
            show_fps=overlay_data.get("show_fps", True),
            show_cpu=overlay_data.get("show_cpu", True),
            show_gpu=overlay_data.get("show_gpu", True),
            show_ram=overlay_data.get("show_ram", True),
            show_temps=overlay_data.get("show_temps", True),
        )
        
        optimizer = OptimizerConfig(
            processes_to_terminate=optimizer_data.get("processes_to_terminate", 
                ["OneDrive.exe", "Cortana.exe", "SearchUI.exe"]),
            set_high_priority=optimizer_data.get("set_high_priority", True),
            clear_ram=optimizer_data.get("clear_ram", True),
            set_timer_resolution=optimizer_data.get("set_timer_resolution", True),
            timer_resolution_ms=optimizer_data.get("timer_resolution_ms", 0.5),
        )
        
        license = LicenseConfig(
            license_key=license_data.get("license_key", ""),
            is_activated=license_data.get("is_activated", False),
            username=license_data.get("username", ""),
            expiry_date=license_data.get("expiry_date", ""),
        )
        
        return AppConfig(
            auto_start=data.get("auto_start", False),
            minimize_to_tray=data.get("minimize_to_tray", True),
            logging_enabled=data.get("logging_enabled", False),
            overlay=overlay,
            optimizer=optimizer,
            license=license,
            hotkeys=data.get("hotkeys", {
                "toggle_overlay": "F12",
                "toggle_game_mode": "F11",
                "start_benchmark": "F10"
            }),
        )
    
    def check_hotkey_conflict(self, action: str, new_hotkey: str) -> Optional[str]:
        """Check if hotkey conflicts with existing assignments.
        Returns conflicting action name or None if no conflict.
        """
        for existing_action, existing_hotkey in self.config.hotkeys.items():
            if existing_action != action and existing_hotkey == new_hotkey:
                return existing_action
        
        # Also check overlay hotkey
        if action != "toggle_overlay" and new_hotkey == self.config.overlay.hotkey:
            return "toggle_overlay"
        
        return None
    
    def set_hotkey(self, action: str, hotkey: str) -> bool:
        """Set hotkey for action. Returns False if conflict exists."""
        conflict = self.check_hotkey_conflict(action, hotkey)
        if conflict:
            return False
        
        if action == "toggle_overlay":
            self.config.overlay.hotkey = hotkey
        else:
            self.config.hotkeys[action] = hotkey
        
        self.save()
        return True
