"""System tray icon for background operation."""
from pathlib import Path
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Signal

# Asset paths
ASSETS_DIR = Path(__file__).parent / "assets"
ICON_PATH = ASSETS_DIR / "icon_rmcr.ico"


class TrayIcon(QSystemTrayIcon):
    """System tray icon with context menu."""
    
    show_requested = Signal()
    exit_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create icon
        self._create_icon()
        
        # Create context menu
        self._create_menu()
        
        # Connect signals
        self.activated.connect(self._on_activated)
    
    def _create_icon(self):
        """Load icon from assets or create fallback."""
        if ICON_PATH.exists():
            self.setIcon(QIcon(str(ICON_PATH)))
        else:
            # Fallback: create simple icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 0, 0, 0))
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor("#00ff88"))
            painter.setPen(QColor("#00cc6a"))
            painter.drawEllipse(4, 4, 24, 24)
            painter.end()
            
            self.setIcon(QIcon(pixmap))
        
        self.setToolTip("RMCR - Game Performance Monitor")
    
    def _create_menu(self):
        """Create the context menu."""
        menu = QMenu()
        
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.show_requested.emit)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_requested.emit)
        
        self.setContextMenu(menu)
    
    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_requested.emit()
