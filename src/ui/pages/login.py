"""License activation page for KeyAuth authentication."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from pathlib import Path

from src.auth.keyauth import get_keyauth

# Style paths
STYLES_DIR = Path(__file__).parent.parent / "styles"
LOGIN_QSS_PATH = STYLES_DIR / "login.qss"


class LoginPage(QWidget):
    """License activation page with KeyAuth integration."""
    
    login_successful = Signal()
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.setObjectName("loginPage")
        self.keyauth = get_keyauth()
        self.config_manager = config_manager
        self._init_ui()
        self._load_styles()
    
    def _load_styles(self):
        """Load styles from external QSS file."""
        if LOGIN_QSS_PATH.exists():
            with open(LOGIN_QSS_PATH, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Top spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Logo/Title frame
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: transparent;")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.setSpacing(5)
        
        logo_path = Path(__file__).parent.parent / "assets" / "logo_rmcr-no-bg.png"
        if logo_path.exists():
            logo_label = QLabel()
            logo_label.setStyleSheet("background-color: transparent;")
            logo_pixmap = QPixmap(str(logo_path))
            logo_label.setPixmap(logo_pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(logo_label)
            
        title = QLabel("GameRMCR")
        subtitle = QLabel("Game Performance Monitor")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_frame)
        
        # License container
        container = QFrame()
        container.setObjectName("loginContainer")
        container.setFixedWidth(420)
        container.setFixedHeight(300)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(30, 30, 30, 30)
        
        # License title
        license_title = QLabel("License Activation")
        license_title.setObjectName("licenseTitle")
        license_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(license_title)
        
        # License info
        license_info = QLabel("Enter your license key to activate the application")
        license_info.setObjectName("licenseInfo")
        license_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_info.setWordWrap(True)
        container_layout.addWidget(license_info)
        
        container_layout.addSpacing(10)
        
        # License input
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX")
        self.license_input.setMinimumHeight(50)
        self.license_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.license_input.returnPressed.connect(self._on_activate)
        container_layout.addWidget(self.license_input)
        
        # Spacing between input and button
        container_layout.addSpacing(15)
        
        # Activate button
        self.activate_btn = QPushButton("Activate License")
        self.activate_btn.setObjectName("primaryButton")
        self.activate_btn.setMinimumHeight(50)
        self.activate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.activate_btn.clicked.connect(self._on_activate)
        container_layout.addWidget(self.activate_btn)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        container_layout.addWidget(self.status_label)
        
        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Bottom spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Version info
        version_label = QLabel("v1.0 | Powered by KeyAuth")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

    def _on_activate(self):
        """Handle license activation."""
        license_key = self.license_input.text().strip()
        
        if not license_key:
            self._show_status("Please enter a license key", error=True)
            return
        
        self._show_status("Validating license...", error=False)
        self.activate_btn.setEnabled(False)
        self.license_input.setEnabled(False)
        
        # Process events to update UI
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        if self.keyauth.license(license_key):
            self._show_status("License activated successfully!", error=False)
            
            # Save license to config
            if self.config_manager:
                username = getattr(self.keyauth, 'username', '')
                expiry = getattr(self.keyauth, 'expiry', '')
                # Convert expiry to string if it's a datetime object
                if expiry and hasattr(expiry, 'isoformat'):
                    expiry = expiry.isoformat()
                elif expiry:
                    expiry = str(expiry)
                self.config_manager.save_license(license_key, username, expiry)
            
            # Small delay before switching
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self.login_successful.emit)
        else:
            self._show_status(f"Activation failed: {self.keyauth.error_message}", error=True)
            self.activate_btn.setEnabled(True)
            self.license_input.setEnabled(True)
    
    def _show_status(self, message: str, error: bool = False):
        """Show status message."""
        self.status_label.setText(message)
        if error:
            self.status_label.setStyleSheet("color: #ff6b6b; font-size: 13px; background-color: transparent;")
        else:
            self.status_label.setStyleSheet("color: #00ff88; font-size: 13px; background-color: transparent;")
