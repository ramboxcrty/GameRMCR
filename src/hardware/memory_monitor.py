"""Memory (RAM) monitoring using psutil."""
import psutil
from src.models.metrics import MemoryMetrics


class MemoryMonitor:
    """Monitor RAM usage."""
    
    def get_memory_metrics(self) -> MemoryMetrics:
        """Get current memory metrics."""
        try:
            mem = psutil.virtual_memory()
            return MemoryMetrics(
                used_mb=int(mem.used / (1024 * 1024)),
                total_mb=int(mem.total / (1024 * 1024)),
                usage_percent=mem.percent
            )
        except Exception:
            return MemoryMetrics()
