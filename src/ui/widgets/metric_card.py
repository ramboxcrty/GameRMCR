"""Metric card widget for displaying system metrics."""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class MetricCard(QFrame):
    """Card widget displaying a single metric."""
    
    def __init__(self, title: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        self.setFixedSize(140, 110)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("metricTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel("--")
        self.value_label.setObjectName("metricValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Unit
        self.unit = unit
        self.unit_label = QLabel(unit)
        self.unit_label.setObjectName("metricUnit")
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.unit_label)
        
        self._is_unavailable = False
        self._apply_styles()
    
    def set_value(self, value: float, decimals: int = 1):
        """Update the displayed value."""
        if value < 0:
            self._set_unavailable(True)
            self.value_label.setText("N/A")
        else:
            self._set_unavailable(False)
            self.value_label.setText(f"{value:.{decimals}f}")
    
    def set_value_text(self, text: str):
        """Set value as text directly."""
        self._set_unavailable(False)
        self.value_label.setText(text)
    
    def _set_unavailable(self, unavailable: bool):
        """Set unavailable state styling."""
        if unavailable != self._is_unavailable:
            self._is_unavailable = unavailable
            self._apply_styles()
    
    def _apply_styles(self):
        """Apply card styles."""
        if self._is_unavailable:
            value_color = "#555555"
            border_color = "#1a2a4a"
            glow = "none"
        else:
            value_color = "#00ff88"
            border_color = "#0f3460"
            glow = "0 0 15px rgba(0, 255, 136, 0.15)"
        
        self.setStyleSheet(f"""
            #metricCard {{
                background-color: #16213e;
                border-radius: 12px;
                border: 1px solid {border_color};
            }}
            #metricTitle {{
                color: #888888;
                font-size: 12px;
                font-weight: 500;
                background-color: transparent;
            }}
            #metricValue {{
                color: {value_color};
                font-size: 26px;
                font-weight: 600;
                background-color: transparent;
            }}
            #metricUnit {{
                color: #555555;
                font-size: 10px;
                background-color: transparent;
            }}
        """)
