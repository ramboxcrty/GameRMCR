"""Settings page for application configuration."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QGroupBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Signal

from src.models.config import AppConfig


class SettingsPage(QWidget):
    """Page for application settings."""
    
    settings_changed = Signal(AppConfig)
    
    def __init__(self, config: AppConfig = None, parent=None):
        super().__init__(parent)
        self.config = config or AppConfig()
        self._init_ui()
        self._load_config()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # General settings
        general_group = QGroupBox("General")
        general_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        general_layout = QVBoxLayout(general_group)
        
        self.auto_start_check = QCheckBox("Start with Windows")
        self.auto_start_check.setStyleSheet("color: #e0e0e0;")
        self.auto_start_check.stateChanged.connect(self._on_setting_changed)
        general_layout.addWidget(self.auto_start_check)
        
        self.minimize_tray_check = QCheckBox("Minimize to system tray")
        self.minimize_tray_check.setStyleSheet("color: #e0e0e0;")
        self.minimize_tray_check.stateChanged.connect(self._on_setting_changed)
        general_layout.addWidget(self.minimize_tray_check)
        
        self.logging_check = QCheckBox("Enable performance logging")
        self.logging_check.setStyleSheet("color: #e0e0e0;")
        self.logging_check.stateChanged.connect(self._on_setting_changed)
        general_layout.addWidget(self.logging_check)
        
        layout.addWidget(general_group)
        
        # Hotkeys
        hotkey_group = QGroupBox("Hotkeys")
        hotkey_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        # Overlay hotkey
        overlay_layout = QHBoxLayout()
        overlay_layout.addWidget(QLabel("Toggle Overlay:"))
        self.overlay_hotkey = QLineEdit()
        self.overlay_hotkey.setMaximumWidth(100)
        self.overlay_hotkey.setStyleSheet("background-color: #16213e; color: #ffffff; border: 1px solid #0f3460;")
        overlay_layout.addWidget(self.overlay_hotkey)
        overlay_layout.addStretch()
        hotkey_layout.addLayout(overlay_layout)
        
        # Game mode hotkey
        gamemode_layout = QHBoxLayout()
        gamemode_layout.addWidget(QLabel("Toggle Game Mode:"))
        self.gamemode_hotkey = QLineEdit()
        self.gamemode_hotkey.setMaximumWidth(100)
        self.gamemode_hotkey.setStyleSheet("background-color: #16213e; color: #ffffff; border: 1px solid #0f3460;")
        gamemode_layout.addWidget(self.gamemode_hotkey)
        gamemode_layout.addStretch()
        hotkey_layout.addLayout(gamemode_layout)
        
        layout.addWidget(hotkey_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ee5a5a;
            }
        """)
        self.reset_btn.clicked.connect(self._on_reset)
        actions_layout.addWidget(self.reset_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        layout.addStretch()
    
    def _load_config(self):
        """Load config values into UI."""
        self.auto_start_check.setChecked(self.config.auto_start)
        self.minimize_tray_check.setChecked(self.config.minimize_to_tray)
        self.logging_check.setChecked(self.config.logging_enabled)
        self.overlay_hotkey.setText(self.config.overlay.hotkey)
        self.gamemode_hotkey.setText(self.config.hotkeys.get("toggle_game_mode", "F11"))
    
    def _on_setting_changed(self):
        """Handle setting change."""
        self.config.auto_start = self.auto_start_check.isChecked()
        self.config.minimize_to_tray = self.minimize_tray_check.isChecked()
        self.config.logging_enabled = self.logging_check.isChecked()
        self.settings_changed.emit(self.config)
    
    def _on_reset(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = AppConfig()
            self._load_config()
            self.settings_changed.emit(self.config)
    
    def get_config(self) -> AppConfig:
        return self.config
