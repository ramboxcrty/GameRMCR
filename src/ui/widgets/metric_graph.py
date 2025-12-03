"""Metric graph widget for displaying time-series data."""
from collections import deque
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath


class MetricGraph(QFrame):
    """Graph widget displaying metric history over time."""
    
    HISTORY_SECONDS = 60
    
    def __init__(self, title: str, color: str = "#00ff88", max_value: float = 100.0, parent=None):
        super().__init__(parent)
        self.setObjectName("metricGraph")
        self.setMinimumSize(200, 120)
        
        self.title = title
        self.color = QColor(color)
        self.max_value = max_value
        self._data: deque = deque(maxlen=self.HISTORY_SECONDS * 2)  # 2 samples per second
        
        # Initialize with zeros
        for _ in range(self.HISTORY_SECONDS * 2):
            self._data.append(0.0)
        
        self._apply_styles()
    
    def add_value(self, value: float):
        """Add a new value to the graph."""
        self._data.append(min(value, self.max_value))
        self.update()
    
    def get_history_size(self) -> int:
        """Get the number of data points in history."""
        return len(self._data)
    
    def paintEvent(self, event):
        """Custom paint for the graph."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor("#16213e"))
        
        # Draw title
        painter.setPen(QColor("#888888"))
        painter.drawText(10, 20, self.title)
        
        # Draw graph area
        margin = 30
        graph_rect = self.rect().adjusted(margin, margin, -10, -10)
        
        if not self._data or graph_rect.width() <= 0:
            return
        
        # Draw grid lines
        painter.setPen(QPen(QColor("#0f3460"), 1))
        for i in range(5):
            y = graph_rect.top() + (graph_rect.height() * i / 4)
            painter.drawLine(graph_rect.left(), int(y), graph_rect.right(), int(y))
        
        # Draw data line
        if len(self._data) < 2:
            return
        
        path = QPainterPath()
        step = graph_rect.width() / (len(self._data) - 1)
        
        for i, value in enumerate(self._data):
            x = graph_rect.left() + i * step
            y = graph_rect.bottom() - (value / self.max_value) * graph_rect.height()
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        painter.setPen(QPen(self.color, 2))
        painter.drawPath(path)
        
        # Draw current value
        if self._data:
            current = self._data[-1]
            painter.setPen(self.color)
            painter.drawText(graph_rect.right() - 50, 20, f"{current:.1f}")
    
    def _apply_styles(self):
        """Apply graph styles."""
        self.setStyleSheet("""
            #metricGraph {
                background-color: #16213e;
                border-radius: 10px;
                border: 1px solid #0f3460;
            }
        """)
