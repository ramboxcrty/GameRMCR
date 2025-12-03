"""AMD Ryzen temperature monitoring via WMI and registry."""
import ctypes
from pathlib import Path
from typing import Optional

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False


class AMDRyzenMonitor:
    """Monitor AMD Ryzen CPU temperature."""
    
    def __init__(self):
        self._wmi = None
        self._initialized = False
        
        # Try WMI for AMD sensors
        if WMI_AVAILABLE:
            try:
                # Try AMD-specific WMI namespace
                self._wmi = wmi.WMI(namespace="root\\wmi")
                self._initialized = True
            except Exception:
                pass
    
    def get_cpu_temperature(self) -> float:
        """Get AMD CPU temperature."""
        if not self._initialized or not self._wmi:
            return 0.0
        
        try:
            # Try AMD-specific temperature class
            for sensor in self._wmi.query("SELECT * FROM AMDACPI_TEMP"):
                if sensor.CurrentTemperature:
                    # AMD reports in tenths of Kelvin
                    temp_c = (sensor.CurrentTemperature / 10.0) - 273.15
                    if 0 < temp_c < 150:
                        return temp_c
        except Exception:
            pass
        
        # Try generic thermal zone
        try:
            for zone in self._wmi.MSAcpi_ThermalZoneTemperature():
                if zone.CurrentTemperature:
                    temp_c = (zone.CurrentTemperature / 10.0) - 273.15
                    if 0 < temp_c < 150:
                        return temp_c
        except Exception:
            pass
        
        return 0.0


# Global instance
_amd_monitor: Optional[AMDRyzenMonitor] = None


def get_amd_monitor() -> AMDRyzenMonitor:
    """Get or create the global AMD monitor instance."""
    global _amd_monitor
    if _amd_monitor is None:
        _amd_monitor = AMDRyzenMonitor()
    return _amd_monitor
