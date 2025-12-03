"""Games page for selecting and managing monitored games."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QGroupBox,
    QSlider, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from src.core.game_detector import GameDetector


class GameItem(QListWidgetItem):
    """Custom list item for games."""
    
    def __init__(self, exe_name: str, display_name: str = None):
        super().__init__()
        self.exe_name = exe_name
        self.display_name = display_name or exe_name.replace(".exe", "").title()
        self.setText(f"{self.display_name} ({exe_name})")
        self.setCheckState(Qt.CheckState.Checked)


class GamesPage(QWidget):
    """Page for managing game list and color settings."""
    
    games_changed = Signal(list)  # List of enabled game exe names
    saturation_changed = Signal(int)  # Saturation value 0-200
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.game_detector = GameDetector()
        self._init_ui()
        self._load_default_games()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Oyun Yönetimi")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Main content - two columns
        content = QHBoxLayout()
        
        # Left column - Game list
        games_group = QGroupBox("İzlenecek Oyunlar")
        games_group.setStyleSheet("QGroupBox { color: #ffffff; font-size: 14px; }")
        games_layout = QVBoxLayout(games_group)
        
        # Game list
        self.game_list = QListWidget()
        self.game_list.setStyleSheet("""
            QListWidget {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #0f3460;
            }
            QListWidget::item:selected {
                background-color: #0f3460;
            }
        """)
        games_layout.addWidget(self.game_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Oyun Ekle")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: #000000;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00cc6a; }
        """)
        self.add_btn.clicked.connect(self._add_game)
        btn_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("Seçileni Kaldır")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: #ffffff;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #ee5a5a; }
        """)
        self.remove_btn.clicked.connect(self._remove_game)
        btn_layout.addWidget(self.remove_btn)
        
        btn_layout.addStretch()
        games_layout.addLayout(btn_layout)
        
        content.addWidget(games_group)
        
        # Right column - Color settings
        color_group = QGroupBox("Renk Ayarları")
        color_group.setStyleSheet("QGroupBox { color: #ffffff; font-size: 14px; }")
        color_layout = QVBoxLayout(color_group)
        
        # Saturation control
        sat_label = QLabel("Renk Doygunluğu (Saturation)")
        sat_label.setStyleSheet("color: #e0e0e0;")
        color_layout.addWidget(sat_label)
        
        sat_row = QHBoxLayout()
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(0, 200)
        self.saturation_slider.setValue(100)  # 100 = normal
        self.saturation_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #0f3460;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00ff88;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
        """)
        self.saturation_slider.valueChanged.connect(self._on_saturation_changed)
        sat_row.addWidget(self.saturation_slider)
        
        self.saturation_value = QLabel("100%")
        self.saturation_value.setStyleSheet("color: #00ff88; font-size: 16px; min-width: 50px;")
        sat_row.addWidget(self.saturation_value)
        
        color_layout.addLayout(sat_row)
        
        # Saturation description
        sat_desc = QLabel("0% = Siyah-Beyaz, 100% = Normal, 200% = Çok Canlı")
        sat_desc.setStyleSheet("color: #888888; font-size: 11px;")
        color_layout.addWidget(sat_desc)
        
        color_layout.addSpacing(20)
        
        # Enable saturation checkbox
        self.enable_saturation = QCheckBox("Doygunluk Efektini Etkinleştir")
        self.enable_saturation.setStyleSheet("color: #e0e0e0;")
        self.enable_saturation.setChecked(False)
        color_layout.addWidget(self.enable_saturation)
        
        # Vibrance presets
        color_layout.addSpacing(10)
        preset_label = QLabel("Hızlı Ayarlar:")
        preset_label.setStyleSheet("color: #e0e0e0;")
        color_layout.addWidget(preset_label)
        
        preset_row = QHBoxLayout()
        presets = [("Normal", 100), ("Canlı", 130), ("Çok Canlı", 160), ("Maksimum", 200)]
        for name, value in presets:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0f3460;
                    color: #ffffff;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #16213e; }
            """)
            btn.clicked.connect(lambda checked, v=value: self._set_saturation(v))
            preset_row.addWidget(btn)
        
        color_layout.addLayout(preset_row)
        color_layout.addStretch()
        
        content.addWidget(color_group)
        layout.addLayout(content)
        layout.addStretch()
    
    def _load_default_games(self):
        """Load default known games."""
        default_games = [
            ("csgo.exe", "Counter-Strike: GO"),
            ("cs2.exe", "Counter-Strike 2"),
            ("valorant.exe", "Valorant"),
            ("fortnite.exe", "Fortnite"),
            ("gta5.exe", "GTA V"),
            ("minecraft.exe", "Minecraft"),
            ("dota2.exe", "Dota 2"),
            ("leagueoflegends.exe", "League of Legends"),
            ("overwatch.exe", "Overwatch"),
            ("apex_legends.exe", "Apex Legends"),
        ]
        
        for exe, name in default_games:
            item = GameItem(exe, name)
            self.game_list.addItem(item)
    
    def _add_game(self):
        """Add a new game via file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Oyun Seç",
            "C:/Program Files",
            "Executable (*.exe)"
        )
        
        if file_path:
            exe_name = Path(file_path).name
            # Check if already exists
            for i in range(self.game_list.count()):
                item = self.game_list.item(i)
                if isinstance(item, GameItem) and item.exe_name == exe_name:
                    return
            
            item = GameItem(exe_name)
            self.game_list.addItem(item)
            self._emit_games_changed()
    
    def _remove_game(self):
        """Remove selected game."""
        current = self.game_list.currentRow()
        if current >= 0:
            self.game_list.takeItem(current)
            self._emit_games_changed()
    
    def _on_saturation_changed(self, value: int):
        """Handle saturation slider change."""
        self.saturation_value.setText(f"{value}%")
        self.saturation_changed.emit(value)
    
    def _set_saturation(self, value: int):
        """Set saturation to preset value."""
        self.saturation_slider.setValue(value)
    
    def _emit_games_changed(self):
        """Emit list of enabled games."""
        games = []
        for i in range(self.game_list.count()):
            item = self.game_list.item(i)
            if isinstance(item, GameItem) and item.checkState() == Qt.CheckState.Checked:
                games.append(item.exe_name)
        self.games_changed.emit(games)
    
    def get_enabled_games(self) -> list:
        """Get list of enabled game executables."""
        games = []
        for i in range(self.game_list.count()):
            item = self.game_list.item(i)
            if isinstance(item, GameItem) and item.checkState() == Qt.CheckState.Checked:
                games.append(item.exe_name)
        return games
    
    def get_saturation(self) -> int:
        """Get current saturation value."""
        return self.saturation_slider.value()
