"""Network monitoring for ping and bandwidth."""
import psutil
import subprocess
import time
from src.models.metrics import NetworkMetrics


class NetworkMonitor:
    """Monitor network metrics."""
    
    def __init__(self):
        self._last_bytes_sent = 0
        self._last_bytes_recv = 0
        self._last_time = time.time()
        self._initialize_counters()
    
    def _initialize_counters(self):
        """Initialize network counters."""
        try:
            net = psutil.net_io_counters()
            self._last_bytes_sent = net.bytes_sent
            self._last_bytes_recv = net.bytes_recv
            self._last_time = time.time()
        except Exception:
            pass
    
    def get_network_metrics(self) -> NetworkMetrics:
        """Get current network metrics."""
        ping = self._get_ping()
        upload, download = self._get_bandwidth()
        
        return NetworkMetrics(
            ping_ms=ping,
            upload_kbps=upload,
            download_kbps=download
        )
    
    def _get_ping(self, host: str = "8.8.8.8") -> float:
        """Get ping to host in milliseconds."""
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1000", host],
                capture_output=True,
                text=True,
                timeout=2
            )
            output = result.stdout
            # Parse "time=XXms" from output
            if "time=" in output or "time<" in output:
                for part in output.split():
                    if part.startswith("time=") or part.startswith("time<"):
                        time_str = part.replace("time=", "").replace("time<", "").replace("ms", "")
                        return float(time_str)
        except Exception:
            pass
        return 0.0
    
    def _get_bandwidth(self) -> tuple[float, float]:
        """Get upload/download speed in kbps."""
        try:
            net = psutil.net_io_counters()
            current_time = time.time()
            elapsed = current_time - self._last_time
            
            if elapsed > 0:
                bytes_sent_diff = net.bytes_sent - self._last_bytes_sent
                bytes_recv_diff = net.bytes_recv - self._last_bytes_recv
                
                upload_kbps = (bytes_sent_diff / elapsed) * 8 / 1000
                download_kbps = (bytes_recv_diff / elapsed) * 8 / 1000
                
                self._last_bytes_sent = net.bytes_sent
                self._last_bytes_recv = net.bytes_recv
                self._last_time = current_time
                
                return max(0, upload_kbps), max(0, download_kbps)
        except Exception:
            pass
        return 0.0, 0.0
