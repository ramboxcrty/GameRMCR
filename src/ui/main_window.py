"""Main application window with sidebar navigation."""
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QLabel, QFrame,
    QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QAction

# Asset paths
ASSETS_DIR = Path(__file__).parent / "assets"
ICON_PATH = ASSETS_DIR / "icon_rmcr.ico"
LOGO_PATH = ASSETS_DIR / "logo_rmcr-no-bg.png"


class SidebarButton(QPushButton):
    """Custom sidebar navigation button."""
    
    def __init__(self, text: str, icon_name: str = "", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setMinimumHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class Sidebar(QFrame):
    """Sidebar navigation panel."""
    
    page_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(160)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)
        
        # Logo
        if LOGO_PATH.exists():
            logo_label = QLabel()
            logo_pixmap = QPixmap(str(LOGO_PATH))
            logo_label.setPixmap(logo_pixmap.scaledToWidth(120, Qt.TransformationMode.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)
        else:
            title = QLabel("RMCR")
            title.setObjectName("sidebarTitle")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
        layout.addSpacing(20)
        
        # Navigation buttons
        self.buttons = []
        pages = [
            ("Dashboard", 0),
            ("Overlay Editor", 1),
            ("Filters", 2),
            ("System Monitor", 3),
            ("Optimizer", 4),
            ("Settings", 5),
            ("About", 6)
        ]
        
        for text, index in pages:
            btn = SidebarButton(text)
            btn.clicked.connect(lambda checked, i=index: self._on_button_clicked(i))
            self.buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Set first button as active and emit signal
        if self.buttons:
            self.buttons[0].setChecked(True)
            # Emit signal to show first page
            self.page_changed.emit(0)
    
    def _on_button_clicked(self, index: int):
        """Handle navigation button click."""
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.page_changed.emit(index)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, minimize_to_tray: bool = True):
        super().__init__()
        self.setWindowTitle("RMCR - Game Performance Monitor")
        self.setMinimumSize(1000, 700)
        self._minimize_to_tray = minimize_to_tray
        
        # Set window icon
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        
        # Initialize system tray
        self._init_tray_icon()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_frame = QFrame()
        content_frame.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Stacked widget for pages
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        main_layout.addWidget(content_frame, 1)
        
        # Initialize pages (placeholders for now)
        self._init_pages()
        
        # Set initial page to Dashboard (index 0)
        self.stack.setCurrentIndex(0)
        
        # Apply stylesheet
        self._apply_styles()
    
    def _init_pages(self):
        """Initialize page widgets."""
        # Placeholder pages - will be replaced with actual implementations
        pages = ["Dashboard", "Overlay Editor", "System Monitor", "Optimizer", "Settings"]
        for name in pages:
            page = QWidget()
            layout = QVBoxLayout(page)
            label = QLabel(f"{name} Page")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 24px; color: #888;")
            layout.addWidget(label)
            self.stack.addWidget(page)
    
    def _on_page_changed(self, index: int):
        """Handle page navigation."""
        self.stack.setCurrentIndex(index)
    
    def set_page(self, index: int, widget: QWidget):
        """Replace a page widget."""
        old_widget = self.stack.widget(index)
        if old_widget is not None:
            self.stack.removeWidget(old_widget)
            old_widget.deleteLater()
        self.stack.insertWidget(index, widget)
    
    def _init_tray_icon(self):
        """Initialize system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set tray icon
        if ICON_PATH.exists():
            self.tray_icon.setIcon(QIcon(str(ICON_PATH)))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        self.show_action = QAction("Show", self)
        self.show_action.triggered.connect(self._show_window)
        tray_menu.addAction(self.show_action)
        
        # Game Mode toggle
        self.game_mode_action = QAction("Toggle Game Mode", self)
        self.game_mode_action.triggered.connect(self._toggle_game_mode)
        tray_menu.addAction(self.game_mode_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.setToolTip("RMCR - Game Performance Monitor")
        self.tray_icon.show()
    
    def _show_window(self):
        """Show and activate the main window."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.activateWindow()
        self.raise_()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()
    
    def _toggle_game_mode(self):
        """Toggle game mode from tray."""
        # This will be connected to the optimizer
        pass
    
    def _quit_application(self):
        """Quit the application completely."""
        self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self._minimize_to_tray and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "RMCR",
                "Application minimized to tray. Double-click to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.tray_icon.hide()
            event.accept()
    
    def show_tray_notification(self, title: str, message: str, 
                               icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information):
        """Show a notification from the system tray."""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, 3000)
    
    def _apply_styles(self):
        """Apply dark theme stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            #sidebar {
                background-color: #16213e;
                border-right: 1px solid #0f3460;
            }
            #sidebarTitle {
                color: #00ff88;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
            SidebarButton {
                background-color: transparent;
                color: #a0a0a0;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                text-align: left;
                font-size: 14px;
            }
            SidebarButton:hover {
                background-color: #1a1a2e;
                color: #ffffff;
            }
            SidebarButton:checked {
                background-color: #0f3460;
                color: #00ff88;
            }
            #contentArea {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
