"""Optimizer page for game mode controls."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal

from src.models.config import OptimizerConfig
from src.core.optimizer import OptimizationEngine, OptimizationResult


class OptimizerPage(QWidget):
    """Page for game mode optimization controls."""
    
    game_mode_toggled = Signal(bool)
    
    def __init__(self, config: OptimizerConfig = None, parent=None):
        super().__init__(parent)
        self.config = config or OptimizerConfig()
        self.engine = OptimizationEngine(self.config)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Game Optimizer")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Status
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Game Mode: Inactive")
        self.status_label.setStyleSheet("font-size: 18px; color: #888888;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("Activate Game Mode")
        self.activate_btn.setMinimumSize(200, 50)
        self.activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: #000000;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #00cc6a;
            }
        """)
        self.activate_btn.clicked.connect(self._on_activate)
        btn_layout.addWidget(self.activate_btn)
        
        self.deactivate_btn = QPushButton("Deactivate")
        self.deactivate_btn.setMinimumSize(150, 50)
        self.deactivate_btn.setEnabled(False)
        self.deactivate_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: #ffffff;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ee5a5a;
            }
            QPushButton:disabled {
                background-color: #444444;
            }
        """)
        self.deactivate_btn.clicked.connect(self._on_deactivate)
        btn_layout.addWidget(self.deactivate_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Options
        options_group = QGroupBox("Optimization Options")
        options_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        options_layout = QVBoxLayout(options_group)
        
        self.priority_check = QCheckBox("Set High Process Priority")
        self.priority_check.setChecked(self.config.set_high_priority)
        self.priority_check.setStyleSheet("color: #e0e0e0;")
        options_layout.addWidget(self.priority_check)
        
        self.ram_check = QCheckBox("Clear Standby RAM")
        self.ram_check.setChecked(self.config.clear_ram)
        self.ram_check.setStyleSheet("color: #e0e0e0;")
        options_layout.addWidget(self.ram_check)
        
        self.timer_check = QCheckBox("Set Timer Resolution (0.5ms)")
        self.timer_check.setChecked(self.config.set_timer_resolution)
        self.timer_check.setStyleSheet("color: #e0e0e0;")
        options_layout.addWidget(self.timer_check)
        
        layout.addWidget(options_group)
        
        # Log
        log_group = QGroupBox("Optimization Log")
        log_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a15;
                color: #00ff88;
                font-family: Consolas;
                border: 1px solid #0f3460;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
    
    def _on_activate(self):
        """Activate game mode."""
        self.config.set_high_priority = self.priority_check.isChecked()
        self.config.clear_ram = self.ram_check.isChecked()
        self.config.set_timer_resolution = self.timer_check.isChecked()
        
        self.engine.config = self.config
        result = self.engine.activate_game_mode()
        
        self._update_status(True)
        self._log_result("ACTIVATED", result)
        self.game_mode_toggled.emit(True)
    
    def _on_deactivate(self):
        """Deactivate game mode."""
        result = self.engine.deactivate_game_mode()
        
        self._update_status(False)
        self._log_result("DEACTIVATED", result)
        self.game_mode_toggled.emit(False)
    
    def _update_status(self, active: bool):
        """Update UI status."""
        if active:
            self.status_label.setText("Game Mode: Active")
            self.status_label.setStyleSheet("font-size: 18px; color: #00ff88;")
            self.activate_btn.setEnabled(False)
            self.deactivate_btn.setEnabled(True)
        else:
            self.status_label.setText("Game Mode: Inactive")
            self.status_label.setStyleSheet("font-size: 18px; color: #888888;")
            self.activate_btn.setEnabled(True)
            self.deactivate_btn.setEnabled(False)
    
    def _log_result(self, action: str, result: OptimizationResult):
        """Log optimization result."""
        self.log_text.append(f"=== {action} ===")
        for act in result.actions:
            self.log_text.append(f"[{act.result.upper()}] {act.action_type}: {act.target}")
            if act.details:
                self.log_text.append(f"    {act.details}")
        self.log_text.append("")
