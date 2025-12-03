"""MSR (Model Specific Register) reader for CPU temperature.

Requires WinRing0 driver or similar kernel-mode driver.
"""
import ctypes
from pathlib import Path
from typing import Optional


class MSRReader:
    """Read CPU temperature from MSR registers."""
    
    # MSR addresses
    MSR_TEMPERATURE_TARGET = 0x1A2  # Intel
    MSR_THERM_STATUS = 0x19C        # Intel
    
    def __init__(self):
        self._driver = None
        self._initialized = False
        
        # Try to load WinRing0 driver
        possible_paths = [
            Path("WinRing0x64.dll"),
            Path("lib/WinRing0x64.dll"),
            Path("drivers/WinRing0x64.dll"),
        ]
        
        for dll_path in possible_paths:
            if dll_path.exists():
                try:
                    self._driver = ctypes.CDLL(str(dll_path))
                    self._setup_functions()
                    
                    # Initialize driver
                    if self._driver.InitializeOls():
                        self._initialized = True
                        print(f"WinRing0 driver initialized from {dll_path}")
                        break
                except Exception as e:
                    print(f"Failed to load WinRing0 from {dll_path}: {e}")
                    continue
    
    def _setup_functions(self):
        """Setup function signatures."""
        if not self._driver:
            return
        
        # InitializeOls
        self._driver.InitializeOls.restype = ctypes.c_bool
        
        # DeinitializeOls
        self._driver.DeinitializeOls.restype = None
        
        # Rdmsr
        self._driver.Rdmsr.argtypes = [
            ctypes.c_uint32,  # index
            ctypes.POINTER(ctypes.c_uint32),  # eax
            ctypes.POINTER(ctypes.c_uint32),  # edx
        ]
        self._driver.Rdmsr.restype = ctypes.c_bool
    
    def read_msr(self, msr_index: int) -> Optional[int]:
        """Read MSR register."""
        if not self._initialized or not self._driver:
            return None
        
        try:
            eax = ctypes.c_uint32()
            edx = ctypes.c_uint32()
            
            if self._driver.Rdmsr(msr_index, ctypes.byref(eax), ctypes.byref(edx)):
                # Combine eax and edx into 64-bit value
                return (edx.value << 32) | eax.value
        except Exception as e:
            print(f"Error reading MSR {hex(msr_index)}: {e}")
        
        return None
    
    def get_intel_cpu_temperature(self) -> float:
        """Get Intel CPU temperature from MSR."""
        if not self._initialized:
            return 0.0
        
        try:
            # Read temperature target (TjMax)
            target = self.read_msr(self.MSR_TEMPERATURE_TARGET)
            if target is None:
                return 0.0
            
            tj_max = (target >> 16) & 0xFF
            if tj_max == 0:
                tj_max = 100  # Default TjMax
            
            # Read thermal status
            status = self.read_msr(self.MSR_THERM_STATUS)
            if status is None:
                return 0.0
            
            # Digital readout (bits 22:16)
            digital_readout = (status >> 16) & 0x7F
            
            # Temperature = TjMax - Digital Readout
            temperature = tj_max - digital_readout
            
            if 0 < temperature < 150:
                return float(temperature)
        except Exception as e:
            print(f"Error calculating Intel temp from MSR: {e}")
        
        return 0.0
    
    def close(self):
        """Cleanup driver."""
        if self._initialized and self._driver:
            try:
                self._driver.DeinitializeOls()
            except:
                pass
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()


# Global instance
_msr_reader: Optional[MSRReader] = None


def get_msr_reader() -> MSRReader:
    """Get or create the global MSR reader instance."""
    global _msr_reader
    if _msr_reader is None:
        _msr_reader = MSRReader()
    return _msr_reader
