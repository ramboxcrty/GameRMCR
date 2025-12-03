"""Theme manager for overlay customization."""
from pathlib import Path
from typing import Dict, List, Optional
import json

from src.models.config import Theme, OverlayConfig


class ThemeManager:
    """Manage overlay themes and customization.
    
    Allows users to load, create, and apply themes for the overlay.
    """
    
    def __init__(self, themes_dir: Optional[Path] = None):
        """Initialize theme manager.
        
        Args:
            themes_dir: Directory containing theme files
        """
        self.themes_dir = themes_dir or Path("themes")
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        
        # Ensure themes directory exists
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Load themes
        self.load_themes()
    
    def load_themes(self) -> None:
        """Load all themes from themes directory."""
        self.themes = {}
        
        # Load theme files
        if self.themes_dir.exists():
            for theme_file in self.themes_dir.glob("*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    
                    theme = Theme.from_dict(theme_data)
                    self.themes[theme.name] = theme
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error loading theme {theme_file}: {e}")
        
        # If no themes loaded, create defaults
        if not self.themes:
            self._create_default_themes()
    
    def _create_default_themes(self) -> None:
        """Create default themes."""
        # Default theme
        default_theme = Theme(
            name="default",
            colors={
                "fps": "#00FF00",
                "cpu": "#00BFFF",
                "gpu": "#FF6B6B",
                "ram": "#FFD700",
                "temp": "#FF8C00"
            },
            font_family="Segoe UI",
            font_size=14,
            background_color="#1e1e1e",
            opacity=0.8
        )
        self.themes["default"] = default_theme
        self.save_theme(default_theme)
        
        # Dark theme
        dark_theme = Theme(
            name="dark",
            colors={
                "fps": "#4CAF50",
                "cpu": "#2196F3",
                "gpu": "#F44336",
                "ram": "#FFC107",
                "temp": "#FF9800"
            },
            font_family="Consolas",
            font_size=13,
            background_color="#0d0d0d",
            opacity=0.9
        )
        self.themes["dark"] = dark_theme
        self.save_theme(dark_theme)
        
        # Neon theme
        neon_theme = Theme(
            name="neon",
            colors={
                "fps": "#00FF41",
                "cpu": "#00D9FF",
                "gpu": "#FF00FF",
                "ram": "#FFFF00",
                "temp": "#FF6600"
            },
            font_family="Arial",
            font_size=15,
            background_color="#000000",
            opacity=0.7
        )
        self.themes["neon"] = neon_theme
        self.save_theme(neon_theme)
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get a theme by name.
        
        Args:
            name: Theme name
            
        Returns:
            Theme object or None if not found
        """
        return self.themes.get(name)
    
    def get_theme_names(self) -> List[str]:
        """Get list of available theme names.
        
        Returns:
            List of theme names
        """
        return list(self.themes.keys())
    
    def apply_theme(self, theme: Theme) -> OverlayConfig:
        """Apply a theme and return corresponding overlay config.
        
        Args:
            theme: Theme to apply
            
        Returns:
            OverlayConfig with theme settings applied
        """
        self.current_theme = theme
        
        # Create overlay config from theme
        config = OverlayConfig(
            font_family=theme.font_family,
            font_size=theme.font_size,
            color=theme.colors.get("fps", "#00FF00"),
            opacity=theme.opacity
        )
        
        return config
    
    def save_custom_theme(self, theme: Theme) -> None:
        """Save a custom theme.
        
        Args:
            theme: Theme to save
        """
        self.themes[theme.name] = theme
        self.save_theme(theme)
    
    def save_theme(self, theme: Theme) -> None:
        """Save theme to file.
        
        Args:
            theme: Theme to save
        """
        theme_file = self.themes_dir / f"{theme.name}.json"
        
        with open(theme_file, 'w', encoding='utf-8') as f:
            json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
    
    def export_theme(self, theme: Theme, filepath: Path) -> None:
        """Export theme to a specific file.
        
        Args:
            theme: Theme to export
            filepath: Destination file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
    
    def import_theme(self, filepath: Path) -> Theme:
        """Import theme from file.
        
        Args:
            filepath: Source file path
            
        Returns:
            Imported theme
            
        Raises:
            ValueError: If theme file is invalid
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme = Theme.from_dict(theme_data)
            self.themes[theme.name] = theme
            self.save_theme(theme)
            
            return theme
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid theme file: {e}")
    
    def delete_theme(self, name: str) -> bool:
        """Delete a theme.
        
        Args:
            name: Theme name
            
        Returns:
            True if deleted, False if not found or is default
        """
        # Don't allow deleting default themes
        if name in ["default", "dark", "neon"]:
            return False
        
        if name in self.themes:
            del self.themes[name]
            
            # Delete file
            theme_file = self.themes_dir / f"{name}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            return True
        
        return False
    
    def create_theme_from_config(self, name: str, config: OverlayConfig) -> Theme:
        """Create a theme from overlay config.
        
        Args:
            name: Theme name
            config: Overlay configuration
            
        Returns:
            Created theme
        """
        theme = Theme(
            name=name,
            colors={
                "fps": config.color,
                "cpu": config.color,
                "gpu": config.color,
                "ram": config.color,
                "temp": config.color
            },
            font_family=config.font_family,
            font_size=config.font_size,
            background_color="#1e1e1e",
            opacity=config.opacity
        )
        
        return theme
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get currently active theme.
        
        Returns:
            Current theme or None
        """
        return self.current_theme
