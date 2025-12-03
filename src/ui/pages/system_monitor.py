"""System monitor page with detailed hardware info."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QGroupBox
from PySide6.QtCore import Qt

from src.ui.widgets.metric_graph import MetricGraph
from src.models.metrics import SystemMetrics


class SystemMonitorPage(QWidget):
    """Page displaying detailed system monitoring information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("System Monitor")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # CPU Section
        cpu_group = QGroupBox("CPU")
        cpu_group.setStyleSheet("QGroupBox { color: #ffffff; font-size: 16px; }")
        cpu_layout = QHBoxLayout(cpu_group)
        
        cpu_info = QVBoxLayout()
        self.cpu_name = QLabel("CPU: --")
        self.cpu_name.setStyleSheet("color: #e0e0e0;")
        self.cpu_usage = QLabel("Usage: --%")
        self.cpu_usage.setStyleSheet("color: #00ff88; font-size: 18px;")
        self.cpu_temp = QLabel("Temperature: --°C")
        self.cpu_temp.setStyleSheet("color: #ff6b6b;")
        self.cpu_freq = QLabel("Frequency: -- MHz")
        self.cpu_freq.setStyleSheet("color: #e0e0e0;")
        cpu_info.addWidget(self.cpu_name)
        cpu_info.addWidget(self.cpu_usage)
        cpu_info.addWidget(self.cpu_temp)
        cpu_info.addWidget(self.cpu_freq)
        cpu_layout.addLayout(cpu_info)
        
        self.cpu_graph = MetricGraph("CPU %", "#ff6b6b", 100)
        cpu_layout.addWidget(self.cpu_graph)
        
        layout.addWidget(cpu_group)
        
        # GPU Section
        gpu_group = QGroupBox("GPU")
        gpu_group.setStyleSheet("QGroupBox { color: #ffffff; font-size: 16px; }")
        gpu_layout = QHBoxLayout(gpu_group)
        
        gpu_info = QVBoxLayout()
        self.gpu_name = QLabel("GPU: --")
        self.gpu_name.setStyleSheet("color: #e0e0e0;")
        self.gpu_usage = QLabel("Usage: --%")
        self.gpu_usage.setStyleSheet("color: #00ff88; font-size: 18px;")
        self.gpu_temp = QLabel("Temperature: --°C")
        self.gpu_temp.setStyleSheet("color: #ff6b6b;")
        self.gpu_vram = QLabel("VRAM: -- / -- MB")
        self.gpu_vram.setStyleSheet("color: #e0e0e0;")
        gpu_info.addWidget(self.gpu_name)
        gpu_info.addWidget(self.gpu_usage)
        gpu_info.addWidget(self.gpu_temp)
        gpu_info.addWidget(self.gpu_vram)
        gpu_layout.addLayout(gpu_info)
        
        self.gpu_graph = MetricGraph("GPU %", "#4ecdc4", 100)
        gpu_layout.addWidget(self.gpu_graph)
        
        layout.addWidget(gpu_group)
        
        # Memory & Network row
        bottom_layout = QHBoxLayout()
        
        # Memory
        mem_group = QGroupBox("Memory")
        mem_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        mem_layout = QVBoxLayout(mem_group)
        self.ram_usage = QLabel("RAM: -- / -- MB")
        self.ram_usage.setStyleSheet("color: #e0e0e0;")
        self.ram_percent = QLabel("--%")
        self.ram_percent.setStyleSheet("color: #00ff88; font-size: 18px;")
        mem_layout.addWidget(self.ram_usage)
        mem_layout.addWidget(self.ram_percent)
        bottom_layout.addWidget(mem_group)
        
        # Network
        net_group = QGroupBox("Network")
        net_group.setStyleSheet("QGroupBox { color: #ffffff; }")
        net_layout = QVBoxLayout(net_group)
        self.ping = QLabel("Ping: -- ms")
        self.ping.setStyleSheet("color: #e0e0e0;")
        self.upload = QLabel("Upload: -- kbps")
        self.upload.setStyleSheet("color: #e0e0e0;")
        self.download = QLabel("Download: -- kbps")
        self.download.setStyleSheet("color: #e0e0e0;")
        net_layout.addWidget(self.ping)
        net_layout.addWidget(self.upload)
        net_layout.addWidget(self.download)
        bottom_layout.addWidget(net_group)
        
        layout.addLayout(bottom_layout)
        layout.addStretch()
    
    def update_metrics(self, metrics: SystemMetrics):
        """Update all displayed metrics."""
        # CPU
        self.cpu_name.setText(f"CPU: {metrics.cpu.name}")
        self.cpu_usage.setText(f"Usage: {metrics.cpu.usage_percent:.1f}%")
        self.cpu_temp.setText(f"Temperature: {metrics.cpu.temperature:.1f}°C")
        self.cpu_freq.setText(f"Frequency: {metrics.cpu.frequency_mhz} MHz")
        self.cpu_graph.add_value(metrics.cpu.usage_percent)
        
        # GPU
        self.gpu_name.setText(f"GPU: {metrics.gpu.name}")
        self.gpu_usage.setText(f"Usage: {metrics.gpu.usage_percent:.1f}%")
        self.gpu_temp.setText(f"Temperature: {metrics.gpu.temperature:.1f}°C")
        self.gpu_vram.setText(f"VRAM: {metrics.gpu.vram_used_mb} / {metrics.gpu.vram_total_mb} MB")
        self.gpu_graph.add_value(metrics.gpu.usage_percent)
        
        # Memory
        self.ram_usage.setText(f"RAM: {metrics.memory.used_mb} / {metrics.memory.total_mb} MB")
        self.ram_percent.setText(f"{metrics.memory.usage_percent:.1f}%")
        
        # Network
        self.ping.setText(f"Ping: {metrics.network.ping_ms:.1f} ms")
        self.upload.setText(f"Upload: {metrics.network.upload_kbps:.1f} kbps")
        self.download.setText(f"Download: {metrics.network.download_kbps:.1f} kbps")
