"""About page with transparency and diagnostics."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QGroupBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt

from src.core.error_handler import ErrorHandler


class AboutPage(QWidget):
    """About page showing license, active hooks, and diagnostics."""
    
    def __init__(self, error_handler: ErrorHandler):
        super().__init__()
        self.error_handler = error_handler
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Title with version
        from src.version import __version__
        title = QLabel(f"About RMCR v{__version__}")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # License info
        license_group = self.create_license_group()
        layout.addWidget(license_group)
        
        # Active hooks
        hooks_group = self.create_hooks_group()
        layout.addWidget(hooks_group)
        
        # Diagnostics
        diag_group = self.create_diagnostics_group()
        layout.addWidget(diag_group)
        
        # Permissions explanation
        perms_group = self.create_permissions_group()
        layout.addWidget(perms_group)
        
        # Temperature monitoring info
        temp_group = self.create_temperature_info_group()
        layout.addWidget(temp_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_license_group(self) -> QGroupBox:
        """Create license information group."""
        group = QGroupBox("Open Source License")
        layout = QVBoxLayout()
        
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setMaximumHeight(150)
        license_text.setText("""
RMCR - Game Performance Monitor
Copyright (c) 2024

This is an open-source project.
Repository: https://github.com/yourusername/rmcr

MIT License - Free to use, modify, and distribute.
        """.strip())
        layout.addWidget(license_text)
        
        # Repository link button
        repo_btn = QPushButton("Open Repository")
        repo_btn.clicked.connect(self.open_repository)
        layout.addWidget(repo_btn)
        
        group.setLayout(layout)
        return group
    
    def create_hooks_group(self) -> QGroupBox:
        """Create active hooks display group."""
        group = QGroupBox("Active Hooks & Injected DLLs")
        layout = QVBoxLayout()
        
        info_label = QLabel("Currently active DirectX hooks and injected DLLs:")
        info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(info_label)
        
        self.hooks_list = QListWidget()
        self.hooks_list.setMaximumHeight(120)
        layout.addWidget(self.hooks_list)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Hooks List")
        refresh_btn.clicked.connect(self.refresh_hooks)
        layout.addWidget(refresh_btn)
        
        group.setLayout(layout)
        
        # Initial load
        self.refresh_hooks()
        
        return group
    
    def create_diagnostics_group(self) -> QGroupBox:
        """Create diagnostics export group."""
        group = QGroupBox("Diagnostics & Error Logs")
        layout = QVBoxLayout()
        
        # Error summary
        self.error_summary_label = QLabel()
        layout.addWidget(self.error_summary_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        export_diag_btn = QPushButton("Export Diagnostics")
        export_diag_btn.clicked.connect(self.export_diagnostics)
        btn_layout.addWidget(export_diag_btn)
        
        view_errors_btn = QPushButton("View Error Log")
        view_errors_btn.clicked.connect(self.view_error_log)
        btn_layout.addWidget(view_errors_btn)
        
        clear_logs_btn = QPushButton("Clear Old Logs")
        clear_logs_btn.clicked.connect(self.clear_old_logs)
        btn_layout.addWidget(clear_logs_btn)
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        
        # Update summary
        self.update_error_summary()
        
        return group
    
    def create_permissions_group(self) -> QGroupBox:
        """Create permissions explanation group."""
        group = QGroupBox("Administrator Permissions")
        layout = QVBoxLayout()
        
        perms_text = QTextEdit()
        perms_text.setReadOnly(True)
        perms_text.setMaximumHeight(100)
        perms_text.setText("""
Why Administrator Access is Required:

• DirectX Hook Injection: Requires elevated privileges to inject DLL into game processes
• Process Priority Management: Needs admin rights to change process priorities
• Timer Resolution: System-level timer adjustments require admin access
• Hardware Monitoring: Some sensors require elevated access for accurate readings
        """.strip())
        layout.addWidget(perms_text)
        
        group.setLayout(layout)
        return group
    
    def refresh_hooks(self):
        """Refresh the list of active hooks."""
        self.hooks_list.clear()
        
        # TODO: Get actual hooks from overlay manager
        # For now, show placeholder
        self.hooks_list.addItem("DirectX 11 Hook - Present() - Active")
        self.hooks_list.addItem("ImGui Overlay - overlay.dll - Injected")
        self.hooks_list.addItem("No other hooks detected")
    
    def update_error_summary(self):
        """Update error summary display."""
        summary = self.error_handler.get_error_summary()
        
        text = f"Total Errors: {summary['total']}\n"
        if summary['by_level']:
            text += "By Level: " + ", ".join([f"{k}: {v}" for k, v in summary['by_level'].items()])
        else:
            text += "No errors logged"
        
        self.error_summary_label.setText(text)
    
    def export_diagnostics(self):
        """Export diagnostics to file."""
        try:
            filepath = self.error_handler.export_diagnostics()
            QMessageBox.information(
                self,
                "Success",
                f"Diagnostics exported to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export diagnostics:\n{str(e)}"
            )
    
    def view_error_log(self):
        """Open error log file."""
        import subprocess
        import sys
        from pathlib import Path
        
        log_file = Path("logs/errors.log")
        if not log_file.exists():
            QMessageBox.information(self, "Info", "No error log file found.")
            return
        
        try:
            if sys.platform == 'win32':
                subprocess.run(['notepad', str(log_file)])
            else:
                subprocess.run(['xdg-open', str(log_file)])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open log:\n{str(e)}")
    
    def clear_old_logs(self):
        """Clear old error logs."""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Clear error logs older than 7 days?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cleared = self.error_handler.clear_old_logs(days=7)
            self.update_error_summary()
            QMessageBox.information(
                self,
                "Success",
                f"Cleared {cleared} old log entries."
            )
    
    def create_temperature_info_group(self) -> QGroupBox:
        """Create temperature monitoring information group."""
        group = QGroupBox("Temperature Monitoring Setup")
        layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(120)
        info_text.setText("""
CPU Temperature Monitoring:

Windows does not provide direct access to CPU temperature sensors. To enable temperature monitoring:

1. Download OpenHardwareMonitor or LibreHardwareMonitor (recommended)
2. Run it as Administrator
3. Keep it running in the background
4. Restart RMCR

Download Links:
• OpenHardwareMonitor: https://openhardwaremonitor.org/downloads/
• LibreHardwareMonitor: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases

GPU temperature works automatically for NVIDIA GPUs.
        """.strip())
        layout.addWidget(info_text)
        
        # Download buttons
        btn_layout = QHBoxLayout()
        
        ohm_btn = QPushButton("Download OpenHardwareMonitor")
        ohm_btn.clicked.connect(lambda: self.open_url("https://openhardwaremonitor.org/downloads/"))
        btn_layout.addWidget(ohm_btn)
        
        lhm_btn = QPushButton("Download LibreHardwareMonitor")
        lhm_btn.clicked.connect(lambda: self.open_url("https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases"))
        btn_layout.addWidget(lhm_btn)
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
    
    def open_url(self, url: str):
        """Open URL in browser."""
        import webbrowser
        webbrowser.open(url)
    
    def open_repository(self):
        """Open repository in browser."""
        self.open_url("https://github.com/yourusername/rmcr")
