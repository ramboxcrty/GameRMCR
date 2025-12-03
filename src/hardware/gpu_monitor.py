"""GPU monitoring with NVIDIA/AMD/Intel detection."""
from typing import Optional
from src.models.metrics import GPUMetrics

# Try importing GPU libraries
try:
    # Try nvidia-ml-py first (recommended), fallback to pynvml
    try:
        from nvidia_ml_py import nvml as pynvml
    except ImportError:
        import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    pynvml = None

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False


class GPUMonitor:
    """Monitor GPU metrics using multiple methods."""
    
    def __init__(self):
        self._wmi = None
        self._gpu_name = "Unknown"
        self._vendor = "unknown"
        self._nvml_initialized = False
        self._nvml_handle = None
        
        # Try NVIDIA first
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self._nvml_initialized = True
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    self._nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    self._gpu_name = pynvml.nvmlDeviceGetName(self._nvml_handle)
                    if isinstance(self._gpu_name, bytes):
                        self._gpu_name = self._gpu_name.decode('utf-8')
                    self._vendor = "nvidia"
            except Exception as e:
                self._nvml_initialized = False
                print(f"NVML init failed: {e}")
        
        # Fallback to WMI
        if self._vendor == "unknown" and WMI_AVAILABLE:
            try:
                self._wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            except Exception:
                try:
                    self._wmi = wmi.WMI()
                except Exception:
                    pass
            
            self._detect_gpu_wmi()
    
    def _detect_gpu_wmi(self):
        """Detect GPU vendor and name using WMI."""
        if not WMI_AVAILABLE:
            return
        
        try:
            w = wmi.WMI()
            for gpu in w.Win32_VideoController():
                self._gpu_name = gpu.Name or "Unknown"
                name_lower = self._gpu_name.lower()
                if "nvidia" in name_lower:
                    self._vendor = "nvidia"
                elif "amd" in name_lower or "radeon" in name_lower:
                    self._vendor = "amd"
                elif "intel" in name_lower:
                    self._vendor = "intel"
                break
        except Exception:
            pass
    
    def __del__(self):
        """Cleanup NVML on destruction."""
        if self._nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass
    
    def get_gpu_metrics(self) -> GPUMetrics:
        """Get current GPU metrics."""
        # Try NVIDIA first
        if self._nvml_initialized and self._nvml_handle:
            return self._get_nvidia_metrics()
        
        # Try GPUtil
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    return GPUMetrics(
                        usage_percent=gpu.load * 100,
                        temperature=gpu.temperature,
                        vram_used_mb=int(gpu.memoryUsed),
                        vram_total_mb=int(gpu.memoryTotal),
                        name=gpu.name
                    )
            except Exception:
                pass
        
        # Fallback to WMI/OpenHardwareMonitor
        usage = self._get_usage_wmi()
        temperature = self._get_temperature_wmi()
        vram_used, vram_total = self._get_vram_wmi()
        
        return GPUMetrics(
            usage_percent=usage,
            temperature=temperature,
            vram_used_mb=vram_used,
            vram_total_mb=vram_total,
            name=self._gpu_name
        )
    
    def _get_nvidia_metrics(self) -> GPUMetrics:
        """Get metrics from NVIDIA GPU using NVML."""
        try:
            # Usage
            utilization = pynvml.nvmlDeviceGetUtilizationRates(self._nvml_handle)
            usage = float(utilization.gpu)
            
            # Temperature
            temp = pynvml.nvmlDeviceGetTemperature(self._nvml_handle, pynvml.NVML_TEMPERATURE_GPU)
            
            # VRAM
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self._nvml_handle)
            vram_used = int(mem_info.used / (1024 * 1024))
            vram_total = int(mem_info.total / (1024 * 1024))
            
            return GPUMetrics(
                usage_percent=usage,
                temperature=float(temp),
                vram_used_mb=vram_used,
                vram_total_mb=vram_total,
                name=self._gpu_name
            )
        except Exception as e:
            print(f"NVML metrics error: {e}")
            return GPUMetrics(name=self._gpu_name)
    
    def _get_usage_wmi(self) -> float:
        """Get GPU usage percentage from WMI/OpenHardwareMonitor."""
        if self._wmi:
            try:
                sensors = self._wmi.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == "Load" and "GPU" in sensor.Name:
                        return float(sensor.Value)
            except Exception:
                pass
        return 0.0
    
    def _get_temperature_wmi(self) -> float:
        """Get GPU temperature from WMI/OpenHardwareMonitor."""
        if self._wmi:
            try:
                sensors = self._wmi.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == "Temperature" and "GPU" in sensor.Name:
                        return float(sensor.Value)
            except Exception:
                pass
        return 0.0
    
    def _get_vram_wmi(self) -> tuple[int, int]:
        """Get VRAM usage from WMI (used_mb, total_mb)."""
        if self._wmi:
            try:
                sensors = self._wmi.Sensor()
                used = 0
                total = 0
                for sensor in sensors:
                    if "GPU Memory" in sensor.Name:
                        if "Used" in sensor.Name:
                            used = int(sensor.Value)
                        elif "Total" in sensor.Name:
                            total = int(sensor.Value)
                if used or total:
                    return used, total
            except Exception:
                pass
        
        # Fallback: try to get total from Win32_VideoController
        if WMI_AVAILABLE:
            try:
                w = wmi.WMI()
                for gpu in w.Win32_VideoController():
                    if gpu.AdapterRAM:
                        total = int(gpu.AdapterRAM) // (1024 * 1024)
                        return 0, total
            except Exception:
                pass
        
        return 0, 0
