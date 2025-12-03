"""OpenHardwareMonitor/LibreHardwareMonitor wrapper for direct sensor access."""
import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict

try:
    import clr  # pythonnet
    CLR_AVAILABLE = True
except ImportError:
    CLR_AVAILABLE = False


class HardwareMonitorWrapper:
    """Wrapper for OpenHardwareMonitor/LibreHardwareMonitor."""
    
    def __init__(self):
        self._computer = None
        self._initialized = False
        self._ohm_process = None
        self._use_clr = False
        
        # Try to initialize with .NET
        if CLR_AVAILABLE:
            self._try_init_clr()
    
    def _try_init_clr(self) -> bool:
        """Try to initialize using .NET CLR."""
        # Look for OpenHardwareMonitorLib.dll in common locations
        possible_paths = [
            Path("lib/OpenHardwareMonitorLib.dll"),
            Path("OpenHardwareMonitorLib.dll"),
            Path.home() / "OpenHardwareMonitor" / "OpenHardwareMonitorLib.dll",
            Path("C:/Program Files/OpenHardwareMonitor/OpenHardwareMonitorLib.dll"),
        ]
        
        for dll_path in possible_paths:
            if dll_path.exists():
                try:
                    clr.AddReference(str(dll_path.absolute()))
                    from OpenHardwareMonitor import Hardware
                    
                    self._computer = Hardware.Computer()
                    self._computer.CPUEnabled = True
                    self._computer.GPUEnabled = True
                    self._computer.MainboardEnabled = True
                    self._computer.Open()
                    
                    self._initialized = True
                    self._use_clr = True
                    print(f"OpenHardwareMonitor initialized via CLR from {dll_path}")
                    return True
                except Exception as e:
                    print(f"Failed to load OHM from {dll_path}: {e}")
                    continue
        
        return False
    
    def get_cpu_temperature(self) -> float:
        """Get CPU temperature."""
        if self._use_clr and self._computer:
            try:
                for hardware in self._computer.Hardware:
                    hardware.Update()
                    if hardware.HardwareType.ToString() == "CPU":
                        temps = []
                        for sensor in hardware.Sensors:
                            if sensor.SensorType.ToString() == "Temperature":
                                name = sensor.Name.upper()
                                if "PACKAGE" in name or "CORE" in name:
                                    if sensor.Value:
                                        temps.append(float(sensor.Value))
                        
                        if temps:
                            return sum(temps) / len(temps)
            except Exception as e:
                print(f"Error reading CPU temp via CLR: {e}")
        
        return 0.0
    
    def get_gpu_temperature(self) -> float:
        """Get GPU temperature."""
        if self._use_clr and self._computer:
            try:
                for hardware in self._computer.Hardware:
                    hardware.Update()
                    hw_type = hardware.HardwareType.ToString()
                    if "GPU" in hw_type or "GpuNvidia" in hw_type or "GpuAti" in hw_type:
                        for sensor in hardware.Sensors:
                            if sensor.SensorType.ToString() == "Temperature":
                                if sensor.Value:
                                    return float(sensor.Value)
            except Exception as e:
                print(f"Error reading GPU temp via CLR: {e}")
        
        return 0.0
    
    def close(self):
        """Close the hardware monitor."""
        if self._computer:
            try:
                self._computer.Close()
            except:
                pass
        
        if self._ohm_process:
            try:
                self._ohm_process.terminate()
            except:
                pass
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()


# Global instance
_ohm_wrapper: Optional[HardwareMonitorWrapper] = None


def get_ohm_wrapper() -> HardwareMonitorWrapper:
    """Get or create the global OHM wrapper instance."""
    global _ohm_wrapper
    if _ohm_wrapper is None:
        _ohm_wrapper = HardwareMonitorWrapper()
    return _ohm_wrapper
