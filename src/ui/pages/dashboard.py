"""Dashboard page with real-time system metrics."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt

from src.ui.widgets.metric_card import MetricCard
from src.ui.widgets.metric_graph import MetricGraph
from src.models.metrics import SystemMetrics


class DashboardPage(QWidget):
    """Dashboard page displaying real-time system metrics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("RMCR Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Metric cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        self.fps_card = MetricCard("FPS", "frames/sec")
        self.cpu_card = MetricCard("CPU", "%")
        self.gpu_card = MetricCard("GPU", "%")
        self.ram_card = MetricCard("RAM", "MB")
        self.cpu_temp_card = MetricCard("CPU Temp", "°C")
        self.gpu_temp_card = MetricCard("GPU Temp", "°C")
        
        cards_layout.addWidget(self.fps_card)
        cards_layout.addWidget(self.cpu_card)
        cards_layout.addWidget(self.gpu_card)
        cards_layout.addWidget(self.ram_card)
        cards_layout.addWidget(self.cpu_temp_card)
        cards_layout.addWidget(self.gpu_temp_card)
        cards_layout.addStretch(1)
        
        layout.addLayout(cards_layout)
        
        # Graphs row
        graphs_layout = QHBoxLayout()
        graphs_layout.setSpacing(15)
        
        self.fps_graph = MetricGraph("FPS History", "#00ff88", 200)
        self.cpu_graph = MetricGraph("CPU Usage", "#ff6b6b", 100)
        self.gpu_graph = MetricGraph("GPU Usage", "#4ecdc4", 100)
        
        graphs_layout.addWidget(self.fps_graph)
        graphs_layout.addWidget(self.cpu_graph)
        graphs_layout.addWidget(self.gpu_graph)
        
        layout.addLayout(graphs_layout)
        layout.addStretch()
    
    def update_metrics(self, metrics: SystemMetrics, fps: float = 0.0):
        """Update all displayed metrics."""
        # Update cards
        self.fps_card.set_value(fps, 0)
        self.cpu_card.set_value(metrics.cpu.usage_percent)
        self.gpu_card.set_value(metrics.gpu.usage_percent)
        self.ram_card.set_value(metrics.memory.used_mb, 0)
        self.cpu_temp_card.set_value(metrics.cpu.temperature)
        self.gpu_temp_card.set_value(metrics.gpu.temperature)
        
        # Update graphs
        self.fps_graph.add_value(fps)
        self.cpu_graph.add_value(metrics.cpu.usage_percent)
        self.gpu_graph.add_value(metrics.gpu.usage_percent)
