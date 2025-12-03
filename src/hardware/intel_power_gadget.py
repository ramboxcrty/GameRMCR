"""Intel Power Gadget API wrapper for Intel CPU temperature."""
import ctypes
import os
from pathlib import Path
from typing import Optional


class IntelPowerGadget:
    """Wrapper for Intel Power Gadget API."""
    
    def __init__(self):
        self._dll = None
        self._initialized = False
        self._temp_msr = 0
        
        # Try to load Intel Power Gadget DLL
        possible_paths = [
            Path(r"C:\Program Files\Intel\Power Gadget 3.6\EnergyLib64.dll"),
            Path(r"C:\Program Files\Intel\Power Gadget 3.5\EnergyLib64.dll"),
            Path(r"C:\Program Files (x86)\Intel\Power Gadget 3.6\EnergyLib32.dll"),
            Path(r"C:\Program Files (x86)\Intel\Power Gadget 3.5\EnergyLib32.dll"),
        ]
        
        for dll_path in possible_paths:
            if dll_path.exists():
                try:
                    self._dll = ctypes.CDLL(str(dll_path))
                    self._setup_functions()
                    
                    # Initialize
                    result = self._dll.IntelEnergyLibInitialize()
                    if result:
                        self._initialized = True
                        print(f"Intel Power Gadget initialized from {dll_path}")
                        break
                except Exception as e:
                    print(f"Failed to load Intel Power Gadget from {dll_path}: {e}")
                    continue
    
    def _setup_functions(self):
        """Setup function signatures."""
        if not self._dll:
            return
        
        # IntelEnergyLibInitialize
        self._dll.IntelEnergyLibInitialize.restype = ctypes.c_bool
        
        # GetNumMsrs
        self._dll.GetNumMsrs.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self._dll.GetNumMsrs.restype = ctypes.c_bool
        
        # GetMsrName
        self._dll.GetMsrName.argtypes = [ctypes.c_int, ctypes.c_wchar_p]
        self._dll.GetMsrName.restype = ctypes.c_bool
        
        # GetMsrFunc
        self._dll.GetMsrFunc.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self._dll.GetMsrFunc.restype = ctypes.c_bool
        
        # ReadSample
        self._dll.ReadSample.restype = ctypes.c_bool
        
        # GetTemperature
        self._dll.GetTemperature.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
        self._dll.GetTemperature.restype = ctypes.c_bool
    
    def get_cpu_temperature(self) -> float:
        """Get CPU package temperature."""
        if not self._initialized or not self._dll:
            return 0.0
        
        try:
            # Read sample
            if not self._dll.ReadSample():
                return 0.0
            
            # Get temperature (node 0 = package)
            temp = ctypes.c_double()
            if self._dll.GetTemperature(0, ctypes.byref(temp)):
                return float(temp.value)
        except Exception as e:
            print(f"Error reading Intel CPU temp: {e}")
        
        return 0.0
    
    def close(self):
        """Cleanup."""
        if self._initialized and self._dll:
            try:
                # No explicit cleanup needed
                pass
            except:
                pass
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()


# Global instance
_intel_pg: Optional[IntelPowerGadget] = None


def get_intel_power_gadget() -> IntelPowerGadget:
    """Get or create the global Intel Power Gadget instance."""
    global _intel_pg
    if _intel_pg is None:
        _intel_pg = IntelPowerGadget()
    return _intel_pg
