"""Update notification dialog."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class UpdateDialog(QDialog):
    """Dialog to notify user about available updates."""
    
    def __init__(self, update_info: dict, updater, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.updater = updater
        self.skip_version = False
        
        self.setWindowTitle("Update Available")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🎉 New Version Available!")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        current_version = self.updater.current_version
        new_version = self.update_info.get('version', 'Unknown')
        
        version_label = QLabel(
            f"Current Version: <b>{current_version}</b><br>"
            f"New Version: <b style='color: #00ff88;'>{new_version}</b>"
        )
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Changelog
        changelog_label = QLabel("What's New:")
        changelog_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(changelog_label)
        
        changelog = QTextEdit()
        changelog.setReadOnly(True)
        changelog.setPlainText(self.updater.format_changelog(self.update_info))
        changelog.setMaximumHeight(200)
        layout.addWidget(changelog)
        
        # Skip version checkbox
        self.skip_checkbox = QCheckBox(f"Skip this version ({new_version})")
        layout.addWidget(self.skip_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        download_btn = QPushButton("Download Update")
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: #000000;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00dd77;
            }
        """)
        download_btn.clicked.connect(self._on_download)
        button_layout.addWidget(download_btn)
        
        later_btn = QPushButton("Remind Me Later")
        later_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a3e;
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3a3a4e;
            }
        """)
        later_btn.clicked.connect(self.reject)
        button_layout.addWidget(later_btn)
        
        layout.addLayout(button_layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 5px;
                padding: 10px;
            }
            QCheckBox {
                color: #e0e0e0;
            }
        """)
    
    def _on_download(self):
        """Handle download button click."""
        self.skip_version = self.skip_checkbox.isChecked()
        self.updater.open_download_page(self.update_info)
        self.accept()
