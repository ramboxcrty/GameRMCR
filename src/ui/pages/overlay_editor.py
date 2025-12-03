"""Overlay editor page for customizing HUD appearance."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QPushButton, QColorDialog, QFontComboBox, QSpinBox, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from src.models.config import OverlayConfig


class OverlayPreview(QFrame):
    """Preview widget showing overlay appearance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        self.setStyleSheet("background-color: #000000; border-radius: 10px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.preview_label = QLabel("FPS: 60\nCPU: 45%\nGPU: 67%\nRAM: 8192 MB")
        self.preview_label.setStyleSheet("color: #00ff00; font-size: 14px;")
        layout.addWidget(self.preview_label)
        layout.addStretch()
    
    def update_style(self, config: OverlayConfig):
        """Update preview based on config."""
        self.preview_label.setStyleSheet(f"""
            color: {config.color};
            font-family: {config.font_family};
            font-size: {config.font_size}px;
        """)
        self.setWindowOpacity(config.opacity)


class OverlayEditorPage(QWidget):
    """Page for editing overlay appearance."""
    
    config_changed = Signal(OverlayConfig)
    
    def __init__(self, config: OverlayConfig = None, parent=None):
        super().__init__(parent)
        self.config = config or OverlayConfig()
        self._init_ui()
        self._load_config()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout(self)
        layout.setSpacing(30)
        
        # Left side - controls
        controls = QVBoxLayout()
        controls.setSpacing(15)
        
        title = QLabel("Overlay Editor")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        controls.addWidget(title)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        font_layout = QVBoxLayout(font_group)
        
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self._on_font_changed)
        font_layout.addWidget(QLabel("Font Family:"))
        font_layout.addWidget(self.font_combo)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.valueChanged.connect(self._on_size_changed)
        font_layout.addWidget(QLabel("Font Size:"))
        font_layout.addWidget(self.font_size)
        
        controls.addWidget(font_group)
        
        # Color settings
        color_group = QGroupBox("Color Settings")
        color_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        color_layout = QVBoxLayout(color_group)
        
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self._on_color_clicked)
        color_layout.addWidget(self.color_btn)
        
        controls.addWidget(color_group)
        
        # Position settings
        pos_group = QGroupBox("Position")
        pos_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        pos_layout = QVBoxLayout(pos_group)
        
        self.position_combo = QComboBox()
        self.position_combo.addItems(["top-left", "top-right", "bottom-left", "bottom-right", "center"])
        self.position_combo.currentTextChanged.connect(self._on_position_changed)
        pos_layout.addWidget(self.position_combo)
        
        controls.addWidget(pos_group)
        
        # Opacity
        opacity_group = QGroupBox("Opacity")
        opacity_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        opacity_layout = QVBoxLayout(opacity_group)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("80%")
        opacity_layout.addWidget(self.opacity_label)
        
        controls.addWidget(opacity_group)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Right side - preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.preview = OverlayPreview()
        preview_layout.addWidget(self.preview)
        preview_layout.addStretch()
        
        layout.addLayout(preview_layout)
    
    def _load_config(self):
        """Load config values into UI."""
        self.font_size.setValue(self.config.font_size)
        self.position_combo.setCurrentText(self.config.position)
        self.opacity_slider.setValue(int(self.config.opacity * 100))
        self._update_preview()
    
    def _on_font_changed(self, font):
        self.config.font_family = font.family()
        self._update_preview()
    
    def _on_size_changed(self, size):
        self.config.font_size = size
        self._update_preview()
    
    def _on_color_clicked(self):
        color = QColorDialog.getColor(QColor(self.config.color), self)
        if color.isValid():
            self.config.color = color.name()
            self._update_preview()
    
    def _on_position_changed(self, position):
        self.config.position = position
        self._update_preview()
    
    def _on_opacity_changed(self, value):
        self.config.opacity = value / 100.0
        self.opacity_label.setText(f"{value}%")
        self._update_preview()
    
    def _update_preview(self):
        self.preview.update_style(self.config)
        self.config_changed.emit(self.config)
    
    def get_config(self) -> OverlayConfig:
        return self.config
