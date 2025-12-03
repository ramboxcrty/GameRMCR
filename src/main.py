"""RMCR - Game Performance Monitor - Main Application Entry Point."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QStackedWidget, QMainWindow
from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QIcon

from src.ui.main_window import MainWindow, ICON_PATH
from src.ui.tray_icon import TrayIcon
from src.core.updater import check_for_updates_async
from src.version import __version__
from src.ui.pages.dashboard import DashboardPage
from src.ui.pages.overlay_editor import OverlayEditorPage
from src.ui.pages.filters import FiltersPage
from src.ui.pages.system_monitor import SystemMonitorPage
from src.ui.pages.optimizer import OptimizerPage
from src.ui.pages.settings import SettingsPage
from src.ui.pages.about import AboutPage
from src.ui.pages.login import LoginPage
from src.core.monitoring import MonitoringEngine
from src.core.config import ConfigManager
from src.core.fps_calculator import FPSCalculator
from src.core.filter_manager import FilterManager
from src.core.error_handler import ErrorHandler
from src.models.config import AppConfig
from src.auth.keyauth import get_keyauth

# Style paths
STYLES_DIR = Path(__file__).parent / "ui" / "styles"
MAIN_QSS_PATH = STYLES_DIR / "style.qss"

# Set to False to skip login (for development)
REQUIRE_AUTH = False


class MetricsSignalBridge(QObject):
    """Bridge to emit metrics updates in the main Qt thread."""
    metrics_updated = Signal(object, float)  # (SystemMetrics, fps)


class GamePPApp:
    """Main application class."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.metrics_bridge = MetricsSignalBridge()
        self.app.setApplicationName("RMCR")
        self.app.setApplicationDisplayName("RMCR - Game Performance Monitor")
        
        # Set application icon
        if ICON_PATH.exists():
            self.app.setWindowIcon(QIcon(str(ICON_PATH)))
        
        # Apply global dark theme
        self._apply_global_style()
        
        # Initialize config
        config_path = Path("config/user_config.json")
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()
        
        # Initialize KeyAuth
        self.keyauth = get_keyauth()

        # Create root window with stacked widget
        self.root_window = QMainWindow()
        self.root_window.setWindowTitle("RMCR - Game Performance Monitor")
        self.root_window.setMinimumSize(1000, 700)
        if ICON_PATH.exists():
            self.root_window.setWindowIcon(QIcon(str(ICON_PATH)))
        
        self.stack = QStackedWidget()
        self.root_window.setCentralWidget(self.stack)
        
        # Create login page
        self.login_page = LoginPage(config_manager=self.config_manager)
        self.login_page.login_successful.connect(self._on_login_success)
        self.stack.addWidget(self.login_page)
        
        # Main window will be created after login
        self.main_window = None
        self.monitoring_engine = None
        self.fps_calculator = None
        self.tray_icon = None
        self.fps_timer = None
    
    def _apply_global_style(self):
        """Apply global dark theme from QSS file."""
        base_style = """
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
        """
        
        # Load main QSS if exists
        if MAIN_QSS_PATH.exists():
            with open(MAIN_QSS_PATH, 'r', encoding='utf-8') as f:
                base_style += f.read()
        
        self.app.setStyleSheet(base_style)
    
    def _on_login_success(self):
        """Handle successful login."""
        # Initialize main application
        self._init_main_app()
        
        # Switch to main window
        self.stack.setCurrentWidget(self.main_window)
        
        # Start monitoring
        self.monitoring_engine.subscribe(self._on_metrics_update)
        self.monitoring_engine.start()
        
        # Start FPS timer
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self._simulate_fps)
        self.fps_timer.start(16)
    
    def _init_main_app(self):
        """Initialize main application components."""
        # Initialize monitoring
        self.monitoring_engine = MonitoringEngine()
        self.fps_calculator = FPSCalculator()
        
        # Create main window
        self.main_window = MainWindow(minimize_to_tray=self.config.minimize_to_tray)
        self.stack.addWidget(self.main_window)
        
        # Initialize managers
        self.filter_manager = FilterManager()
        self.error_handler = ErrorHandler()
        
        # Create pages
        self.dashboard = DashboardPage()
        self.overlay_editor = OverlayEditorPage(self.config.overlay)
        self.filters = FiltersPage(self.filter_manager)
        self.system_monitor = SystemMonitorPage()
        self.optimizer = OptimizerPage(self.config.optimizer)
        self.settings = SettingsPage(self.config)
        self.about = AboutPage(self.error_handler)
        
        # Set pages in main window
        self.main_window.set_page(0, self.dashboard)
        self.main_window.set_page(1, self.overlay_editor)
        self.main_window.set_page(2, self.filters)
        self.main_window.set_page(3, self.system_monitor)
        self.main_window.set_page(4, self.optimizer)
        self.main_window.set_page(5, self.settings)
        self.main_window.set_page(6, self.about)
        
        # Ensure Dashboard is shown initially
        self.main_window.stack.setCurrentIndex(0)
        
        # Connect signals
        self.overlay_editor.config_changed.connect(self._on_overlay_config_changed)
        self.settings.settings_changed.connect(self._on_settings_changed)
        self.metrics_bridge.metrics_updated.connect(self._update_ui_metrics)
        
        # System tray
        self.tray_icon = TrayIcon()
        self.tray_icon.show_requested.connect(self._show_window)
        self.tray_icon.exit_requested.connect(self._exit_app)
        self.tray_icon.show()
        
        # Check if temperature monitoring is available
        self._check_temperature_monitoring()
        
        # Check for updates
        self._check_for_updates()

    def _on_metrics_update(self, metrics):
        """Handle metrics update from monitoring engine (called from worker thread)."""
        if self.fps_calculator:
            fps = self.fps_calculator.get_current_fps()
            # Emit signal to update UI in main thread
            self.metrics_bridge.metrics_updated.emit(metrics, fps)
    
    def _update_ui_metrics(self, metrics, fps):
        """Update UI with metrics (called in main Qt thread)."""
        # Debug: print metrics to verify data is coming through
        print(f"UI Update - CPU: {metrics.cpu.usage_percent:.1f}%, GPU: {metrics.gpu.usage_percent:.1f}%, FPS: {fps:.1f}")
        if self.dashboard:
            self.dashboard.update_metrics(metrics, fps)
        if self.system_monitor:
            self.system_monitor.update_metrics(metrics)
    
    def _simulate_fps(self):
        """Simulate FPS recording (in real app, comes from DX hook)."""
        if self.fps_calculator:
            # Simulate ~60 FPS (16.67ms frame time)
            import random
            frame_time = 16.67 + random.uniform(-2, 2)  # Add some variance
            self.fps_calculator.add_frame(frame_time)
    
    def _on_overlay_config_changed(self, config):
        """Handle overlay config change."""
        self.config.overlay = config
        self.config_manager.config = self.config
        self.config_manager.save()
    
    def _on_settings_changed(self, config):
        """Handle settings change."""
        self.config = config
        self.config_manager.config = self.config
        self.config_manager.save()
    
    def _show_window(self):
        """Show main window."""
        self.root_window.show()
        self.root_window.activateWindow()
    
    def _check_for_updates(self):
        """Check for updates in background."""
        def on_update_available(update_info, updater):
            if update_info:
                # Show update dialog in main thread
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self._show_update_dialog(update_info, updater))
        
        check_for_updates_async(on_update_available, self.config_manager)
    
    def _show_update_dialog(self, update_info, updater):
        """Show update dialog."""
        try:
            from src.ui.dialogs.update_dialog import UpdateDialog
            dialog = UpdateDialog(update_info, updater, self.main_window)
            result = dialog.exec()
            
            if dialog.skip_version:
                # Save skipped version to config
                self.config.skipped_version = update_info.get('version', '')
                self.config_manager.save()
        except Exception as e:
            print(f"Error showing update dialog: {e}")
    
    def _check_temperature_monitoring(self):
        """Check if temperature monitoring is available and show info if not."""
        # Wait a bit for first metrics
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self._show_temp_warning_if_needed)
    
    def _show_temp_warning_if_needed(self):
        """Show warning if temperature monitoring is not available."""
        # Check if user wants to see the warning
        if not self.config.show_temp_warning:
            return
        
        if self.monitoring_engine:
            metrics = self.monitoring_engine.get_current_metrics()
            if metrics and metrics.cpu.temperature == 0.0:
                # CPU temp not available
                from PySide6.QtWidgets import QMessageBox
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Temperature Monitoring")
                msg.setText("CPU Temperature Monitoring Not Available")
                msg.setInformativeText(
                    "To enable CPU temperature monitoring:\n\n"
                    "1. Download OpenHardwareMonitor or LibreHardwareMonitor\n"
                    "2. Run it as Administrator\n"
                    "3. Keep it running in the background\n"
                    "4. Restart RMCR\n\n"
                    "See the About page for download links.\n\n"
                    "GPU temperature works automatically for NVIDIA GPUs."
                )
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                # Don't show again checkbox
                dont_show = msg.addButton("Don't show again", QMessageBox.ButtonRole.ActionRole)
                
                msg.exec()
                
                if msg.clickedButton() == dont_show:
                    # Save preference
                    self.config.show_temp_warning = False
                    self.config_manager.save()
    
    def _exit_app(self):
        """Exit the application."""
        if self.monitoring_engine:
            self.monitoring_engine.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        """Run the application."""
        # Initialize KeyAuth
        if REQUIRE_AUTH:
            if not self.keyauth.init():
                print(f"KeyAuth init failed: {self.keyauth.error_message}")
            
            # Check if license is already saved
            if self.config_manager.is_license_activated():
                license_info = self.config_manager.get_license()
                # Try to validate saved license
                if self.keyauth.license(license_info.license_key):
                    # License valid, skip login
                    self._init_main_app()
                    self.stack.setCurrentWidget(self.main_window)
                    self.monitoring_engine.subscribe(self._on_metrics_update)
                    self.monitoring_engine.start()
                    self.fps_timer = QTimer()
                    self.fps_timer.timeout.connect(self._simulate_fps)
                    self.fps_timer.start(16)
            
            self.root_window.show()
        else:
            # Skip login for development
            self._init_main_app()
            self.stack.setCurrentWidget(self.main_window)
            self.monitoring_engine.subscribe(self._on_metrics_update)
            self.monitoring_engine.start()
            self.fps_timer = QTimer()
            self.fps_timer.timeout.connect(self._simulate_fps)
            self.fps_timer.start(16)
            self.root_window.show()
        
        return self.app.exec()


def main():
    """Application entry point."""
    app = GamePPApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
