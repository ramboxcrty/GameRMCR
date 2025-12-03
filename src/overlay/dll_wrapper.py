"""
Native DLL wrapper for DirectX overlay.

Bu modül C++ ile yazılmış GamePPOverlay.dll dosyasını Python'dan kullanmak için
ctypes wrapper sağlar.
"""
import ctypes
from ctypes import c_bool, c_float, c_int, c_char_p
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OverlayDLL:
    """Wrapper for GamePPOverlay.dll native library."""
    
    def __init__(self, dll_path: Optional[Path] = None):
        self._dll = None
        self._loaded = False
        self._dll_path = dll_path or self._find_dll()
    
    def _find_dll(self) -> Optional[Path]:
        """Find the DLL in common locations."""
        search_paths = [
            Path("native/build/bin/GamePPOverlay.dll"),
            Path("native/build/Release/GamePPOverlay.dll"),
            Path("native/build/Debug/GamePPOverlay.dll"),
            Path("bin/GamePPOverlay.dll"),
            Path("GamePPOverlay.dll"),
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def load(self) -> bool:
        """Load the DLL."""
        if self._loaded:
            return True
        
        if not self._dll_path or not self._dll_path.exists():
            logger.warning(f"DLL not found at {self._dll_path}")
            return False
        
        try:
            self._dll = ctypes.CDLL(str(self._dll_path))
            self._setup_functions()
            self._loaded = True
            logger.info(f"Loaded DLL from {self._dll_path}")
            return True
        except OSError as e:
            logger.error(f"Failed to load DLL: {e}")
            return False
    
    def _setup_functions(self):
        """Set up function signatures."""
        if not self._dll:
            return
        
        # Initialize
        self._dll.Initialize.restype = c_bool
        self._dll.Initialize.argtypes = []
        
        # Shutdown
        self._dll.Shutdown.restype = None
        self._dll.Shutdown.argtypes = []
        
        # SetMetrics
        self._dll.SetMetrics.restype = None
        self._dll.SetMetrics.argtypes = [c_float, c_float, c_float, c_float, c_int, c_int]
        
        # GetCurrentFPS
        self._dll.GetCurrentFPS.restype = c_float
        self._dll.GetCurrentFPS.argtypes = []
        
        # GetFrameTime
        self._dll.GetFrameTime.restype = c_float
        self._dll.GetFrameTime.argtypes = []
        
        # SetOverlayVisible
        self._dll.SetOverlayVisible.restype = None
        self._dll.SetOverlayVisible.argtypes = [c_bool]
        
        # SetOverlayPosition
        self._dll.SetOverlayPosition.restype = None
        self._dll.SetOverlayPosition.argtypes = [c_int, c_int]
        
        # SetOverlayOpacity
        self._dll.SetOverlayOpacity.restype = None
        self._dll.SetOverlayOpacity.argtypes = [c_float]
        
        # IsOverlayVisible
        self._dll.IsOverlayVisible.restype = c_bool
        self._dll.IsOverlayVisible.argtypes = []
        
        # SetOverlayColor
        self._dll.SetOverlayColor.restype = None
        self._dll.SetOverlayColor.argtypes = [c_float, c_float, c_float, c_float]
        
        # SetOverlayFontSize
        self._dll.SetOverlayFontSize.restype = None
        self._dll.SetOverlayFontSize.argtypes = [c_int]
        
        # SetOverlayShowFPS
        self._dll.SetOverlayShowFPS.restype = None
        self._dll.SetOverlayShowFPS.argtypes = [c_bool]
        
        # SetOverlayShowCPU
        self._dll.SetOverlayShowCPU.restype = None
        self._dll.SetOverlayShowCPU.argtypes = [c_bool]
        
        # SetOverlayShowGPU
        self._dll.SetOverlayShowGPU.restype = None
        self._dll.SetOverlayShowGPU.argtypes = [c_bool]
        
        # SetOverlayShowRAM
        self._dll.SetOverlayShowRAM.restype = None
        self._dll.SetOverlayShowRAM.argtypes = [c_bool]
        
        # SetOverlayShowTemps
        self._dll.SetOverlayShowTemps.restype = None
        self._dll.SetOverlayShowTemps.argtypes = [c_bool]
        
        # GetVersion
        self._dll.GetVersion.restype = c_char_p
        self._dll.GetVersion.argtypes = []
    
    def initialize(self) -> bool:
        """Initialize the overlay hook."""
        if not self._loaded:
            if not self.load():
                return False
        return self._dll.Initialize()
    
    def shutdown(self):
        """Shutdown the overlay."""
        if self._loaded and self._dll:
            self._dll.Shutdown()
    
    def set_metrics(self, cpu_usage: float, cpu_temp: float,
                    gpu_usage: float, gpu_temp: float,
                    ram_mb: int, vram_mb: int):
        """Update metrics displayed in overlay."""
        if self._loaded and self._dll:
            self._dll.SetMetrics(cpu_usage, cpu_temp, gpu_usage, gpu_temp, ram_mb, vram_mb)
    
    def get_fps(self) -> float:
        """Get current FPS from hook."""
        if self._loaded and self._dll:
            return self._dll.GetCurrentFPS()
        return 0.0
    
    def get_frame_time(self) -> float:
        """Get current frame time in ms."""
        if self._loaded and self._dll:
            return self._dll.GetFrameTime()
        return 0.0
    
    def set_visible(self, visible: bool):
        """Set overlay visibility."""
        if self._loaded and self._dll:
            self._dll.SetOverlayVisible(visible)
    
    def is_visible(self) -> bool:
        """Check if overlay is visible."""
        if self._loaded and self._dll:
            return self._dll.IsOverlayVisible()
        return False
    
    def set_position(self, x: int, y: int):
        """Set overlay position."""
        if self._loaded and self._dll:
            self._dll.SetOverlayPosition(x, y)
    
    def set_opacity(self, opacity: float):
        """Set overlay opacity (0.0 - 1.0)."""
        if self._loaded and self._dll:
            self._dll.SetOverlayOpacity(opacity)
    
    def set_color(self, r: float, g: float, b: float, a: float = 1.0):
        """Set overlay text color (RGBA, 0.0 - 1.0)."""
        if self._loaded and self._dll:
            self._dll.SetOverlayColor(r, g, b, a)
    
    def set_font_size(self, size: int):
        """Set overlay font size."""
        if self._loaded and self._dll:
            self._dll.SetOverlayFontSize(size)
    
    def set_show_fps(self, show: bool):
        """Enable/disable FPS display."""
        if self._loaded and self._dll:
            self._dll.SetOverlayShowFPS(show)
    
    def set_show_cpu(self, show: bool):
        """Enable/disable CPU display."""
        if self._loaded and self._dll:
            self._dll.SetOverlayShowCPU(show)
    
    def set_show_gpu(self, show: bool):
        """Enable/disable GPU display."""
        if self._loaded and self._dll:
            self._dll.SetOverlayShowGPU(show)
    
    def set_show_ram(self, show: bool):
        """Enable/disable RAM display."""
        if self._loaded and self._dll:
            self._dll.SetOverlayShowRAM(show)
    
    def set_show_temps(self, show: bool):
        """Enable/disable temperature display."""
        if self._loaded and self._dll:
            self._dll.SetOverlayShowTemps(show)
    
    def get_version(self) -> str:
        """Get DLL version string."""
        if self._loaded and self._dll:
            return self._dll.GetVersion().decode('utf-8')
        return "N/A"
    
    @property
    def is_loaded(self) -> bool:
        """Check if DLL is loaded."""
        return self._loaded


# Singleton instance
_overlay_dll: Optional[OverlayDLL] = None


def get_overlay_dll() -> OverlayDLL:
    """Get the singleton OverlayDLL instance."""
    global _overlay_dll
    if _overlay_dll is None:
        _overlay_dll = OverlayDLL()
    return _overlay_dll
