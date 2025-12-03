"""Filter manager for visual enhancements per game/program."""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

from src.models.config import FilterConfig, GameFilterProfile


class FilterManager:
    """Manage visual filters and game-specific filter profiles.
    
    Allows users to configure different filter settings (vibrance, sharpening,
    brightness, contrast) for different games/programs.
    """
    
    def __init__(self, profiles_file: Optional[Path] = None):
        """Initialize filter manager.
        
        Args:
            profiles_file: Path to game filter profiles JSON file
        """
        self.profiles_file = profiles_file or Path("config/game_filter_profiles.json")
        self.current_config: FilterConfig = FilterConfig()
        self.profiles: Dict[str, GameFilterProfile] = {}
        self.current_game: Optional[str] = None
        self.presets: Dict[str, FilterConfig] = {}
        
        # Load profiles if file exists
        if self.profiles_file.exists():
            self.load_profiles()
        
        # Initialize default presets
        self._init_default_presets()
    
    def _init_default_presets(self) -> None:
        """Initialize default filter presets."""
        self.presets = {
            "Vibrant": FilterConfig(vibrance=50.0, enabled=True),
            "Sharp": FilterConfig(sharpening=40.0, enabled=True),
            "Bright": FilterConfig(brightness=20.0, enabled=True),
            "High Contrast": FilterConfig(contrast=30.0, enabled=True),
            "Gaming": FilterConfig(vibrance=30.0, sharpening=20.0, brightness=10.0, enabled=True),
            "Cinematic": FilterConfig(vibrance=20.0, contrast=15.0, brightness=-5.0, enabled=True),
        }
    
    def apply_filter_config(self, config: FilterConfig) -> None:
        """Apply a filter configuration.
        
        Args:
            config: Filter configuration to apply
        """
        if not config.is_valid():
            raise ValueError("Invalid filter configuration")
        
        self.current_config = config
    
    def disable_all_filters(self) -> None:
        """Disable all filters and reset to defaults."""
        self.current_config = FilterConfig(enabled=False)
    
    def validate_filter_values(self, config: FilterConfig) -> List[str]:
        """Validate filter configuration values.
        
        Args:
            config: Filter configuration to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not (0.0 <= config.vibrance <= 100.0):
            errors.append(f"Vibrance must be between 0-100%, got {config.vibrance}")
        
        if not (0.0 <= config.sharpening <= 100.0):
            errors.append(f"Sharpening must be between 0-100%, got {config.sharpening}")
        
        if not (-50.0 <= config.brightness <= 50.0):
            errors.append(f"Brightness must be between -50% to +50%, got {config.brightness}")
        
        if not (-50.0 <= config.contrast <= 50.0):
            errors.append(f"Contrast must be between -50% to +50%, got {config.contrast}")
        
        return errors
    
    def save_preset(self, name: str, config: FilterConfig) -> None:
        """Save a filter configuration as a preset.
        
        Args:
            name: Preset name
            config: Filter configuration to save
        """
        if not config.is_valid():
            raise ValueError("Invalid filter configuration")
        
        self.presets[name] = config
    
    def load_preset(self, name: str) -> Optional[FilterConfig]:
        """Load a filter preset by name.
        
        Args:
            name: Preset name
            
        Returns:
            Filter configuration or None if not found
        """
        return self.presets.get(name)
    
    def get_preset_names(self) -> List[str]:
        """Get list of available preset names.
        
        Returns:
            List of preset names
        """
        return list(self.presets.keys())
    
    def create_game_profile(self, game_name: str, process_name: str, 
                           filters: Optional[FilterConfig] = None) -> GameFilterProfile:
        """Create a filter profile for a specific game.
        
        Args:
            game_name: Display name of the game
            process_name: Process executable name (e.g., "game.exe")
            filters: Filter configuration (uses current if None)
            
        Returns:
            Created game filter profile
        """
        if filters is None:
            filters = self.current_config
        
        profile = GameFilterProfile(
            game_name=game_name,
            process_name=process_name,
            filters=filters,
            last_used=datetime.now().isoformat()
        )
        
        self.profiles[process_name] = profile
        return profile
    
    def get_game_profile(self, process_name: str) -> Optional[GameFilterProfile]:
        """Get filter profile for a specific game.
        
        Args:
            process_name: Process executable name
            
        Returns:
            Game filter profile or None if not found
        """
        return self.profiles.get(process_name)
    
    def apply_game_profile(self, process_name: str) -> bool:
        """Apply filter profile for a specific game.
        
        Args:
            process_name: Process executable name
            
        Returns:
            True if profile was found and applied, False otherwise
        """
        profile = self.get_game_profile(process_name)
        if profile:
            self.apply_filter_config(profile.filters)
            self.current_game = process_name
            
            # Update last used timestamp
            profile.last_used = datetime.now().isoformat()
            return True
        
        return False
    
    def update_current_game_profile(self, filters: FilterConfig) -> None:
        """Update filter settings for currently active game.
        
        Args:
            filters: New filter configuration
        """
        if self.current_game and self.current_game in self.profiles:
            self.profiles[self.current_game].filters = filters
            self.profiles[self.current_game].last_used = datetime.now().isoformat()
            self.apply_filter_config(filters)
    
    def delete_game_profile(self, process_name: str) -> bool:
        """Delete a game filter profile.
        
        Args:
            process_name: Process executable name
            
        Returns:
            True if profile was deleted, False if not found
        """
        if process_name in self.profiles:
            del self.profiles[process_name]
            if self.current_game == process_name:
                self.current_game = None
            return True
        return False
    
    def get_all_profiles(self) -> List[GameFilterProfile]:
        """Get all game filter profiles.
        
        Returns:
            List of all game filter profiles
        """
        return list(self.profiles.values())
    
    def save_profiles(self) -> None:
        """Save all game filter profiles to file."""
        # Ensure directory exists
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert profiles to dict
        profiles_data = {
            process_name: profile.to_dict()
            for process_name, profile in self.profiles.items()
        }
        
        # Save to file
        with open(self.profiles_file, 'w', encoding='utf-8') as f:
            json.dump(profiles_data, f, indent=2, ensure_ascii=False)
    
    def load_profiles(self) -> None:
        """Load game filter profiles from file."""
        if not self.profiles_file.exists():
            return
        
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)
            
            # Convert dict to profiles
            self.profiles = {
                process_name: GameFilterProfile.from_dict(data)
                for process_name, data in profiles_data.items()
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading filter profiles: {e}")
            self.profiles = {}
    
    def get_current_config(self) -> FilterConfig:
        """Get current filter configuration.
        
        Returns:
            Current filter configuration
        """
        return self.current_config
    
    def is_enabled(self) -> bool:
        """Check if filters are currently enabled.
        
        Returns:
            True if filters are enabled
        """
        return self.current_config.enabled
