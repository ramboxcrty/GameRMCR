"""
Python-based overlay window (alternative to DirectX hook).

Bu overlay DirectX hook yerine şeffaf bir pencere kullanır.
Avantajları:
- DLL injection gerektirmez
- Anti-cheat ile sorun yaşamaz
- Kolay kurulum

Dezavantajları:
- Tam ekran exclusive modda görünmez
- Borderless/Windowed modda çalışır
"""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QBrush

from src.models.metrics import SystemMetrics
from src.models.config import OverlayConfig


class PythonOverlay(QWidget):
    """Transparent overlay window for displaying metrics."""
    
    def __init__(self, config: OverlayConfig = None):
        super().__init__()
        self.config = config or OverlayConfig()
        self._metrics: SystemMetrics = None
        self._fps: float = 0.0
        
        self._setup_window()
        self._init_ui()
        self.apply_config(self.config)
    
    def _setup_window(self):
        """Configure window properties for overlay."""
        # Frameless, always on top, transparent, tool window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        
        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Don't show in taskbar
        self.setWindowFlag(Qt.WindowType.SubWindow)
    
    def _init_ui(self):
        """Initialize overlay UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(2)
        
        # Create labels for each metric
        self.fps_label = QLabel("FPS: --")
        self.cpu_label = QLabel("CPU: --%")
        self.gpu_label = QLabel("GPU: --%")
        self.ram_label = QLabel("RAM: -- MB")
        self.cpu_temp_label = QLabel("CPU: --°C")
        self.gpu_temp_label = QLabel("GPU: --°C")
        
        self.labels = [
            self.fps_label,
            self.cpu_label,
            self.gpu_label,
            self.ram_label,
            self.cpu_temp_label,
            self.gpu_temp_label
        ]
        
        for label in self.labels:
            layout.addWidget(label)
        
        self.setFixedSize(200, 150)
    
    def apply_config(self, config: OverlayConfig):
        """Apply overlay configuration."""
        self.config = config
        
        # Apply font and color
        font = QFont(config.font_family, config.font_size)
        font.setBold(True)
        
        style = f"""
            QLabel {{
                color: {config.color};
                background-color: rgba(0, 0, 0, 150);
                padding: 2px 5px;
                border-radius: 3px;
            }}
        """
        
        for label in self.labels:
            label.setFont(font)
            label.setStyleSheet(style)
        
        # Apply opacity
        self.setWindowOpacity(config.opacity)
        
        # Apply position
        self._apply_position(config.position)
        
        # Show/hide based on config
        self.fps_label.setVisible(config.show_fps)
        self.cpu_label.setVisible(config.show_cpu)
        self.gpu_label.setVisible(config.show_gpu)
        self.ram_label.setVisible(config.show_ram)
        self.cpu_temp_label.setVisible(config.show_temps)
        self.gpu_temp_label.setVisible(config.show_temps)
    
    def _apply_position(self, position: str):
        """Move overlay to specified screen position."""
        screen = QApplication.primaryScreen().geometry()
        
        if position == "top-left":
            self.move(20, 20)
        elif position == "top-right":
            self.move(screen.width() - self.width() - 20, 20)
        elif position == "bottom-left":
            self.move(20, screen.height() - self.height() - 60)
        elif position == "bottom-right":
            self.move(screen.width() - self.width() - 20, 
                     screen.height() - self.height() - 60)
        elif position == "center":
            self.move((screen.width() - self.width()) // 2, 50)
    
    def update_metrics(self, metrics: SystemMetrics, fps: float = 0.0):
        """Update displayed metrics."""
        self._metrics = metrics
        self._fps = fps
        
        self.fps_label.setText(f"FPS: {fps:.0f}")
        self.cpu_label.setText(f"CPU: {metrics.cpu.usage_percent:.1f}%")
        self.gpu_label.setText(f"GPU: {metrics.gpu.usage_percent:.1f}%")
        self.ram_label.setText(f"RAM: {metrics.memory.used_mb} MB")
        self.cpu_temp_label.setText(f"CPU: {metrics.cpu.temperature:.0f}°C")
        self.gpu_temp_label.setText(f"GPU: {metrics.gpu.temperature:.0f}°C")
    
    def toggle_visibility(self):
        """Toggle overlay visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()


class OverlayManager:
    """
    Overlay yöneticisi - DirectX hook veya Python overlay seçimi.
    
    OVERLAY NASIL ÇALIŞIR:
    
    1. DirectX Hook Yöntemi (C++ DLL):
       - Oyunun DirectX Present() fonksiyonuna hook atılır
       - Her frame'de ImGui ile overlay çizilir
       - Tam ekran dahil her modda çalışır
       - Anti-cheat tarafından engellenebilir
       - DLL injection gerektirir
    
    2. Python Overlay Yöntemi (Bu dosya):
       - Şeffaf, always-on-top pencere oluşturulur
       - Borderless/Windowed modda çalışır
       - Tam ekran exclusive modda görünmez
       - Anti-cheat ile sorun yaşamaz
       - Kolay ve güvenli
    
    Kullanım:
        manager = OverlayManager()
        manager.set_mode("python")  # veya "directx"
        manager.show()
        manager.update_metrics(metrics, fps)
    """
    
    def __init__(self, config: OverlayConfig = None):
        self.config = config or OverlayConfig()
        self._python_overlay: PythonOverlay = None
        self._mode = "python"  # "python" or "directx"
        self._visible = False
    
    def set_mode(self, mode: str):
        """Set overlay mode: 'python' or 'directx'."""
        self._mode = mode
    
    def initialize(self):
        """Initialize the overlay based on mode."""
        if self._mode == "python":
            self._python_overlay = PythonOverlay(self.config)
        elif self._mode == "directx":
            # DirectX hook initialization would go here
            # Requires loading the C++ DLL
            pass
    
    def show(self):
        """Show the overlay."""
        self._visible = True
        if self._mode == "python" and self._python_overlay:
            self._python_overlay.show()
    
    def hide(self):
        """Hide the overlay."""
        self._visible = False
        if self._mode == "python" and self._python_overlay:
            self._python_overlay.hide()
    
    def toggle(self):
        """Toggle overlay visibility."""
        if self._visible:
            self.hide()
        else:
            self.show()
    
    def update_metrics(self, metrics: SystemMetrics, fps: float = 0.0):
        """Update overlay with new metrics."""
        if self._mode == "python" and self._python_overlay:
            self._python_overlay.update_metrics(metrics, fps)
    
    def apply_config(self, config: OverlayConfig):
        """Apply new configuration."""
        self.config = config
        if self._mode == "python" and self._python_overlay:
            self._python_overlay.apply_config(config)
    
    @property
    def is_visible(self) -> bool:
        return self._visible
