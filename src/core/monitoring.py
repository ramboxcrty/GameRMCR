"""Monitoring Engine for collecting system metrics."""
import threading
import time
from datetime import datetime
from typing import Callable, List, Optional

from src.models.metrics import SystemMetrics
from src.hardware.cpu_monitor import CPUMonitor
from src.hardware.gpu_monitor import GPUMonitor
from src.hardware.memory_monitor import MemoryMonitor
from src.hardware.disk_monitor import DiskMonitor
from src.hardware.network_monitor import NetworkMonitor


class MonitoringEngine:
    """Engine for collecting and distributing system metrics."""
    
    def __init__(self, polling_interval: float = 0.5):
        self.polling_interval = polling_interval
        self._subscribers: List[Callable[[SystemMetrics], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_metrics: Optional[SystemMetrics] = None
        self._lock = threading.Lock()
        
        # Initialize monitors
        self._cpu_monitor = CPUMonitor()
        self._gpu_monitor = GPUMonitor()
        self._memory_monitor = MemoryMonitor()
        self._disk_monitor = DiskMonitor()
        self._network_monitor = NetworkMonitor()
    
    def start(self) -> None:
        """Start the monitoring engine."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the monitoring engine."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
    
    def subscribe(self, callback: Callable[[SystemMetrics], None]) -> None:
        """Subscribe to metric updates."""
        with self._lock:
            self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[SystemMetrics], None]) -> None:
        """Unsubscribe from metric updates."""
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent metrics snapshot."""
        with self._lock:
            return self._current_metrics
    
    def _polling_loop(self) -> None:
        """Main polling loop that collects metrics."""
        while self._running:
            try:
                metrics = self._collect_metrics()
                
                with self._lock:
                    self._current_metrics = metrics
                    subscribers = self._subscribers.copy()
                
                # Notify subscribers
                for callback in subscribers:
                    try:
                        callback(metrics)
                    except Exception as e:
                        # Log error but don't stop monitoring
                        import sys
                        print(f"Error in subscriber callback: {e}", file=sys.stderr)
                
            except Exception as e:
                # Log error but continue polling
                import sys
                print(f"Error in polling loop: {e}", file=sys.stderr)
            
            time.sleep(self.polling_interval)
    
    def _collect_metrics(self) -> SystemMetrics:
        """Collect all system metrics."""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu=self._cpu_monitor.get_cpu_metrics(),
            gpu=self._gpu_monitor.get_gpu_metrics(),
            memory=self._memory_monitor.get_memory_metrics(),
            disk=self._disk_monitor.get_disk_metrics(),
            network=self._network_monitor.get_network_metrics()
        )
    
    @property
    def is_running(self) -> bool:
        """Check if the engine is running."""
        return self._running
