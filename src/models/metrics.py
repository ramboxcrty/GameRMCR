"""Data models for system metrics."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class CPUMetrics:
    """CPU performance metrics."""
    usage_percent: float = 0.0
    temperature: float = 0.0
    core_count: int = 0
    frequency_mhz: int = 0
    name: str = "Unknown"
    
    def is_valid(self) -> bool:
        return 0 <= self.usage_percent <= 100 and self.temperature >= 0


@dataclass
class GPUMetrics:
    """GPU performance metrics."""
    usage_percent: float = 0.0
    temperature: float = 0.0
    vram_used_mb: int = 0
    vram_total_mb: int = 0
    name: str = "Unknown"
    
    def is_valid(self) -> bool:
        return (0 <= self.usage_percent <= 100 and 
                self.temperature >= 0 and 
                self.vram_used_mb >= 0)


@dataclass
class MemoryMetrics:
    """RAM memory metrics."""
    used_mb: int = 0
    total_mb: int = 0
    usage_percent: float = 0.0
    
    def is_valid(self) -> bool:
        return (0 <= self.usage_percent <= 100 and 
                self.used_mb >= 0 and 
                self.total_mb >= 0)


@dataclass
class DiskMetrics:
    """Disk/SSD metrics."""
    temperature: float = 0.0
    name: str = "Unknown"
    
    def is_valid(self) -> bool:
        return self.temperature >= 0


@dataclass
class NetworkMetrics:
    """Network performance metrics."""
    ping_ms: float = 0.0
    upload_kbps: float = 0.0
    download_kbps: float = 0.0
    
    def is_valid(self) -> bool:
        return (self.ping_ms >= 0 and 
                self.upload_kbps >= 0 and 
                self.download_kbps >= 0)


@dataclass
class SystemMetrics:
    """Complete system metrics snapshot."""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu: CPUMetrics = field(default_factory=CPUMetrics)
    gpu: GPUMetrics = field(default_factory=GPUMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    disk: DiskMetrics = field(default_factory=DiskMetrics)
    network: NetworkMetrics = field(default_factory=NetworkMetrics)
    
    def is_valid(self) -> bool:
        """Check if all metrics are valid."""
        return (self.cpu.is_valid() and 
                self.gpu.is_valid() and 
                self.memory.is_valid() and 
                self.disk.is_valid() and 
                self.network.is_valid())


@dataclass
class FPSPercentiles:
    """FPS percentile metrics."""
    fps_1_percent_low: float = 0.0
    fps_0_1_percent_low: float = 0.0
    
    def is_valid(self) -> bool:
        """Check if percentiles are valid."""
        return self.fps_0_1_percent_low <= self.fps_1_percent_low


@dataclass
class LogEntry:
    """Single log entry for benchmark logging."""
    timestamp: datetime
    fps: float
    frame_time: float
    fps_1_percent_low: float
    fps_0_1_percent_low: float
    cpu_usage: float
    cpu_temp: float
    gpu_usage: float
    gpu_temp: float
    ram_usage: int
    vram_usage: int
    
    def is_complete(self) -> bool:
        """Check if all required fields are present."""
        return all([
            self.timestamp is not None,
            self.fps >= 0,
            self.frame_time >= 0,
            self.fps_1_percent_low >= 0,
            self.fps_0_1_percent_low >= 0,
            0 <= self.cpu_usage <= 100,
            self.cpu_temp >= 0,
            0 <= self.gpu_usage <= 100,
            self.gpu_temp >= 0,
            self.ram_usage >= 0,
            self.vram_usage >= 0
        ])


@dataclass
class BenchmarkStatistics:
    """Benchmark session statistics."""
    min_fps: float = 0.0
    max_fps: float = 0.0
    avg_fps: float = 0.0
    fps_1_percent_low: float = 0.0
    fps_0_1_percent_low: float = 0.0
    avg_frame_time: float = 0.0
    duration_seconds: float = 0.0
    total_frames: int = 0
    frame_drops: List[int] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Validate statistics consistency."""
        if self.total_frames == 0:
            return True
        return self.min_fps <= self.fps_0_1_percent_low <= self.fps_1_percent_low <= self.avg_fps <= self.max_fps


@dataclass
class OptimizationResult:
    """Result of an optimization operation."""
    success: bool = False
    terminated_processes: List[str] = field(default_factory=list)
    freed_ram_mb: int = 0
    errors: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if result is valid."""
        return isinstance(self.success, bool)


@dataclass
class OptimizationStatus:
    """Current optimization status."""
    game_mode_active: bool = False
    optimized_process: Optional[str] = None
    original_priorities: dict = field(default_factory=dict)
    terminated_processes: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if status is valid."""
        return isinstance(self.game_mode_active, bool)
