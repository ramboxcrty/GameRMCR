"""Filters page for visual enhancements."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QComboBox, QGroupBox, QCheckBox, QLineEdit,
    QListWidget, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal

from src.core.filter_manager import FilterManager
from src.models.config import FilterConfig


class FiltersPage(QWidget):
    """Page for configuring visual filters per game."""
    
    filters_changed = Signal(FilterConfig)
    
    def __init__(self, filter_manager: FilterManager):
        super().__init__()
        self.filter_manager = filter_manager
        self.init_ui()
        self.load_current_filters()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Visual Filters")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Game profile selection
        profile_group = self.create_profile_group()
        layout.addWidget(profile_group)
        
        # Filter controls
        filter_group = self.create_filter_group()
        layout.addWidget(filter_group)
        
        # Presets
        preset_group = self.create_preset_group()
        layout.addWidget(preset_group)
        
        # Apply/Reset buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Filters")
        self.apply_btn.clicked.connect(self.apply_filters)
        button_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.clicked.connect(self.reset_filters)
        button_layout.addWidget(self.reset_btn)
        
        self.disable_btn = QPushButton("Disable All Filters")
        self.disable_btn.clicked.connect(self.disable_filters)
        button_layout.addWidget(self.disable_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def create_profile_group(self) -> QGroupBox:
        """Create game profile selection group."""
        group = QGroupBox("Game Profile")
        layout = QVBoxLayout()
        
        # Profile list
        profile_layout = QHBoxLayout()
        
        self.profile_list = QComboBox()
        self.profile_list.addItem("Default (All Games)")
        self.profile_list.currentTextChanged.connect(self.on_profile_changed)
        profile_layout.addWidget(QLabel("Active Profile:"))
        profile_layout.addWidget(self.profile_list)
        
        layout.addLayout(profile_layout)
        
        # Profile management buttons
        btn_layout = QHBoxLayout()
        
        self.new_profile_btn = QPushButton("New Profile")
        self.new_profile_btn.clicked.connect(self.create_new_profile)
        btn_layout.addWidget(self.new_profile_btn)
        
        self.save_profile_btn = QPushButton("Save Profile")
        self.save_profile_btn.clicked.connect(self.save_current_profile)
        btn_layout.addWidget(self.save_profile_btn)
        
        self.delete_profile_btn = QPushButton("Delete Profile")
        self.delete_profile_btn.clicked.connect(self.delete_current_profile)
        btn_layout.addWidget(self.delete_profile_btn)
        
        layout.addLayout(btn_layout)
        
        # Current game info
        self.current_game_label = QLabel("No game detected")
        self.current_game_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.current_game_label)
        
        group.setLayout(layout)
        return group
    
    def create_filter_group(self) -> QGroupBox:
        """Create filter controls group."""
        group = QGroupBox("Filter Settings")
        layout = QVBoxLayout()
        
        # Enable checkbox
        self.enable_checkbox = QCheckBox("Enable Filters")
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        layout.addWidget(self.enable_checkbox)
        
        # Vibrance slider
        self.vibrance_slider = self.create_slider_control(
            "Vibrance (Color Saturation)", 0, 100, layout
        )
        
        # Sharpening slider
        self.sharpening_slider = self.create_slider_control(
            "Sharpening (Image Clarity)", 0, 100, layout
        )
        
        # Brightness slider
        self.brightness_slider = self.create_slider_control(
            "Brightness", -50, 50, layout
        )
        
        # Contrast slider
        self.contrast_slider = self.create_slider_control(
            "Contrast", -50, 50, layout
        )
        
        group.setLayout(layout)
        return group
    
    def create_slider_control(self, label: str, min_val: int, max_val: int, 
                             parent_layout: QVBoxLayout) -> QSlider:
        """Create a labeled slider control."""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label with value
        label_layout = QHBoxLayout()
        label_widget = QLabel(label)
        value_label = QLabel("0")
        value_label.setMinimumWidth(40)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        label_layout.addWidget(label_widget)
        label_layout.addStretch()
        label_layout.addWidget(value_label)
        layout.addLayout(label_layout)
        
        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(0)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(10)
        
        # Update label when slider moves
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        
        layout.addWidget(slider)
        container.setLayout(layout)
        parent_layout.addWidget(container)
        
        return slider
    
    def create_preset_group(self) -> QGroupBox:
        """Create preset selection group."""
        group = QGroupBox("Presets")
        layout = QHBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Select Preset...")
        for preset_name in self.filter_manager.get_preset_names():
            self.preset_combo.addItem(preset_name)
        
        self.preset_combo.currentTextChanged.connect(self.on_preset_selected)
        layout.addWidget(self.preset_combo)
        
        self.save_preset_btn = QPushButton("Save as Preset")
        self.save_preset_btn.clicked.connect(self.save_as_preset)
        layout.addWidget(self.save_preset_btn)
        
        group.setLayout(layout)
        return group
    
    def load_current_filters(self):
        """Load current filter settings into UI."""
        config = self.filter_manager.get_current_config()
        
        self.enable_checkbox.setChecked(config.enabled)
        self.vibrance_slider.setValue(int(config.vibrance))
        self.sharpening_slider.setValue(int(config.sharpening))
        self.brightness_slider.setValue(int(config.brightness))
        self.contrast_slider.setValue(int(config.contrast))
        
        # Load game profiles
        self.refresh_profile_list()
    
    def refresh_profile_list(self):
        """Refresh the game profile list."""
        current_text = self.profile_list.currentText()
        
        # Block signals to prevent recursion
        self.profile_list.blockSignals(True)
        
        self.profile_list.clear()
        self.profile_list.addItem("Default (All Games)")
        
        for profile in self.filter_manager.get_all_profiles():
            self.profile_list.addItem(f"{profile.game_name} ({profile.process_name})")
        
        # Restore selection
        index = self.profile_list.findText(current_text)
        if index >= 0:
            self.profile_list.setCurrentIndex(index)
        
        # Unblock signals
        self.profile_list.blockSignals(False)
    
    def get_current_filter_config(self) -> FilterConfig:
        """Get filter configuration from UI controls."""
        return FilterConfig(
            vibrance=float(self.vibrance_slider.value()),
            sharpening=float(self.sharpening_slider.value()),
            brightness=float(self.brightness_slider.value()),
            contrast=float(self.contrast_slider.value()),
            enabled=self.enable_checkbox.isChecked()
        )
    
    def apply_filters(self):
        """Apply current filter settings."""
        config = self.get_current_filter_config()
        
        # Validate
        errors = self.filter_manager.validate_filter_values(config)
        if errors:
            QMessageBox.warning(self, "Invalid Settings", "\n".join(errors))
            return
        
        # Apply
        self.filter_manager.apply_filter_config(config)
        self.filters_changed.emit(config)
        
        QMessageBox.information(self, "Success", "Filters applied successfully!")
    
    def reset_filters(self):
        """Reset filters to default."""
        self.vibrance_slider.setValue(0)
        self.sharpening_slider.setValue(0)
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.enable_checkbox.setChecked(False)
    
    def disable_filters(self):
        """Disable all filters."""
        self.filter_manager.disable_all_filters()
        self.enable_checkbox.setChecked(False)
        self.filters_changed.emit(self.filter_manager.get_current_config())
        
        QMessageBox.information(self, "Success", "All filters disabled!")
    
    def on_enable_changed(self, state):
        """Handle enable checkbox state change."""
        enabled = state == Qt.CheckState.Checked.value
        
        # Enable/disable sliders
        self.vibrance_slider.setEnabled(enabled)
        self.sharpening_slider.setEnabled(enabled)
        self.brightness_slider.setEnabled(enabled)
        self.contrast_slider.setEnabled(enabled)
    
    def on_preset_selected(self, preset_name: str):
        """Handle preset selection."""
        if preset_name == "Select Preset...":
            return
        
        preset = self.filter_manager.load_preset(preset_name)
        if preset:
            self.vibrance_slider.setValue(int(preset.vibrance))
            self.sharpening_slider.setValue(int(preset.sharpening))
            self.brightness_slider.setValue(int(preset.brightness))
            self.contrast_slider.setValue(int(preset.contrast))
            self.enable_checkbox.setChecked(preset.enabled)
    
    def save_as_preset(self):
        """Save current settings as a preset."""
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            config = self.get_current_filter_config()
            self.filter_manager.save_preset(name, config)
            
            # Refresh preset list
            self.preset_combo.addItem(name)
            
            QMessageBox.information(self, "Success", f"Preset '{name}' saved!")
    
    def create_new_profile(self):
        """Create a new game profile."""
        game_name, ok1 = QInputDialog.getText(self, "New Profile", "Game name:")
        if not ok1 or not game_name:
            return
        
        process_name, ok2 = QInputDialog.getText(self, "New Profile", 
                                                  "Process name (e.g., game.exe):")
        if not ok2 or not process_name:
            return
        
        # Create profile with current settings
        config = self.get_current_filter_config()
        self.filter_manager.create_game_profile(game_name, process_name, config)
        self.filter_manager.save_profiles()
        
        # Refresh list
        self.refresh_profile_list()
        
        QMessageBox.information(self, "Success", 
                               f"Profile created for {game_name}!")
    
    def save_current_profile(self):
        """Save current settings to active profile."""
        current_text = self.profile_list.currentText()
        if current_text == "Default (All Games)":
            QMessageBox.information(self, "Info", 
                                   "Default profile is automatically saved.")
            return
        
        # Extract process name from combo text
        if "(" in current_text and ")" in current_text:
            process_name = current_text.split("(")[1].split(")")[0]
            config = self.get_current_filter_config()
            
            profile = self.filter_manager.get_game_profile(process_name)
            if profile:
                profile.filters = config
                self.filter_manager.save_profiles()
                QMessageBox.information(self, "Success", "Profile saved!")
    
    def delete_current_profile(self):
        """Delete the currently selected profile."""
        current_text = self.profile_list.currentText()
        if current_text == "Default (All Games)":
            QMessageBox.warning(self, "Error", "Cannot delete default profile.")
            return
        
        # Extract process name
        if "(" in current_text and ")" in current_text:
            process_name = current_text.split("(")[1].split(")")[0]
            
            reply = QMessageBox.question(self, "Confirm Delete",
                                        f"Delete profile for {current_text}?",
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.filter_manager.delete_game_profile(process_name)
                self.filter_manager.save_profiles()
                self.refresh_profile_list()
                QMessageBox.information(self, "Success", "Profile deleted!")
    
    def on_profile_changed(self, profile_text: str):
        """Handle profile selection change."""
        if profile_text == "Default (All Games)":
            self.load_current_filters()
            return
        
        # Extract process name and load profile
        if "(" in profile_text and ")" in profile_text:
            process_name = profile_text.split("(")[1].split(")")[0]
            profile = self.filter_manager.get_game_profile(process_name)
            
            if profile:
                config = profile.filters
                self.vibrance_slider.setValue(int(config.vibrance))
                self.sharpening_slider.setValue(int(config.sharpening))
                self.brightness_slider.setValue(int(config.brightness))
                self.contrast_slider.setValue(int(config.contrast))
                self.enable_checkbox.setChecked(config.enabled)
    
    def update_current_game(self, game_name: str, process_name: str):
        """Update UI to show currently detected game.
        
        Args:
            game_name: Display name of the game
            process_name: Process executable name
        """
        self.current_game_label.setText(f"Detected: {game_name} ({process_name})")
        self.current_game_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        # Auto-apply profile if exists
        if self.filter_manager.apply_game_profile(process_name):
            self.load_current_filters()
            
            # Select in combo
            for i in range(self.profile_list.count()):
                if process_name in self.profile_list.itemText(i):
                    self.profile_list.setCurrentIndex(i)
                    break
