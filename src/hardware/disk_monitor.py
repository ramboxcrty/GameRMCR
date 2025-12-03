"""Disk/SSD temperature monitoring."""
from src.models.metrics import DiskMetrics

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False


class DiskMonitor:
    """Monitor disk temperature."""
    
    def __init__(self):
        self._wmi = None
        if WMI_AVAILABLE:
            try:
                self._wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            except Exception:
                pass
    
    def get_disk_metrics(self) -> DiskMetrics:
        """Get disk temperature metrics."""
        temperature = self._get_temperature()
        name = self._get_disk_name()
        
        return DiskMetrics(
            temperature=temperature,
            name=name
        )
    
    def _get_temperature(self) -> float:
        """Get disk temperature."""
        if self._wmi:
            try:
                sensors = self._wmi.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == "Temperature":
                        if "HDD" in sensor.Name or "SSD" in sensor.Name:
                            return float(sensor.Value)
            except Exception:
                pass
        return 0.0
    
    def _get_disk_name(self) -> str:
        """Get primary disk name."""
        if WMI_AVAILABLE:
            try:
                w = wmi.WMI()
                for disk in w.Win32_DiskDrive():
                    return disk.Model or "Unknown"
            except Exception:
                pass
        return "Unknown"
