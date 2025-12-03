"""Game optimization engine."""
import psutil
import ctypes
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from src.models.config import OptimizerConfig


@dataclass
class OptimizationAction:
    """Record of an optimization action."""
    action_type: str  # 'terminate', 'priority', 'timer', 'ram'
    target: str
    result: str  # 'success', 'failed', 'skipped'
    details: str = ""


@dataclass
class OptimizationResult:
    """Result of optimization operations."""
    success: bool
    terminated_processes: List[str] = field(default_factory=list)
    freed_ram_mb: int = 0
    errors: List[str] = field(default_factory=list)
    actions: List[OptimizationAction] = field(default_factory=list)


class OptimizationEngine:
    """Engine for game mode optimization."""
    
    def __init__(self, config: OptimizerConfig):
        self.config = config
        self._original_priorities: Dict[int, int] = {}
        self._original_timer_resolution: Optional[int] = None
        self._game_mode_active = False
        self._actions_log: List[OptimizationAction] = []
    
    def activate_game_mode(self, game_pid: Optional[int] = None) -> OptimizationResult:
        """Activate game mode optimizations."""
        result = OptimizationResult(success=True)
        self._actions_log.clear()
        
        # Terminate background processes
        if self.config.processes_to_terminate:
            terminated = self._terminate_processes(self.config.processes_to_terminate)
            result.terminated_processes = terminated
        
        # Set game process priority
        if game_pid and self.config.set_high_priority:
            self._set_process_priority(game_pid, psutil.HIGH_PRIORITY_CLASS)
        
        # Clear RAM
        if self.config.clear_ram:
            freed = self._clear_standby_ram()
            result.freed_ram_mb = freed
        
        # Set timer resolution
        if self.config.set_timer_resolution:
            self._set_timer_resolution(self.config.timer_resolution_ms)
        
        self._game_mode_active = True
        result.actions = self._actions_log.copy()
        return result
    
    def deactivate_game_mode(self) -> OptimizationResult:
        """Deactivate game mode and restore original state."""
        result = OptimizationResult(success=True)
        self._actions_log.clear()
        
        # Restore process priorities
        self._restore_priorities()
        
        # Restore timer resolution
        if self._original_timer_resolution is not None:
            self._restore_timer_resolution()
        
        self._game_mode_active = False
        result.actions = self._actions_log.copy()
        return result

    
    def _terminate_processes(self, process_names: List[str]) -> List[str]:
        """Terminate processes by name."""
        terminated = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] in process_names:
                    proc.terminate()
                    terminated.append(proc.info['name'])
                    self._log_action('terminate', proc.info['name'], 'success')
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self._log_action('terminate', proc.info['name'], 'failed', str(e))
            except Exception as e:
                self._log_action('terminate', proc.info['name'], 'failed', str(e))
        return terminated
    
    def _set_process_priority(self, pid: int, priority: int) -> bool:
        """Set process priority and store original."""
        try:
            proc = psutil.Process(pid)
            self._original_priorities[pid] = proc.nice()
            proc.nice(priority)
            self._log_action('priority', str(pid), 'success', f'Set to {priority}')
            return True
        except Exception as e:
            self._log_action('priority', str(pid), 'failed', str(e))
            return False
    
    def _restore_priorities(self) -> None:
        """Restore original process priorities."""
        for pid, priority in self._original_priorities.items():
            try:
                proc = psutil.Process(pid)
                proc.nice(priority)
                self._log_action('priority', str(pid), 'success', f'Restored to {priority}')
            except Exception as e:
                self._log_action('priority', str(pid), 'failed', str(e))
        self._original_priorities.clear()
    
    def _clear_standby_ram(self) -> int:
        """Clear standby RAM. Returns MB freed."""
        try:
            # This requires admin privileges on Windows
            # Using EmptyWorkingSet for current process as demo
            mem_before = psutil.virtual_memory().available
            
            # Try to clear working set
            kernel32 = ctypes.windll.kernel32
            current_process = kernel32.GetCurrentProcess()
            kernel32.SetProcessWorkingSetSize(current_process, -1, -1)
            
            mem_after = psutil.virtual_memory().available
            freed_mb = max(0, (mem_after - mem_before) // (1024 * 1024))
            
            self._log_action('ram', 'standby', 'success', f'Freed {freed_mb}MB')
            return freed_mb
        except Exception as e:
            self._log_action('ram', 'standby', 'failed', str(e))
            return 0
    
    def _set_timer_resolution(self, resolution_ms: float) -> bool:
        """Set Windows timer resolution."""
        try:
            # Convert ms to 100-nanosecond intervals
            resolution_100ns = int(resolution_ms * 10000)
            ntdll = ctypes.windll.ntdll
            
            # Store original
            current = ctypes.c_ulong()
            ntdll.NtQueryTimerResolution(ctypes.byref(ctypes.c_ulong()), 
                                         ctypes.byref(ctypes.c_ulong()),
                                         ctypes.byref(current))
            self._original_timer_resolution = current.value
            
            # Set new resolution
            ntdll.NtSetTimerResolution(resolution_100ns, True, ctypes.byref(current))
            self._log_action('timer', str(resolution_ms), 'success')
            return True
        except Exception as e:
            self._log_action('timer', str(resolution_ms), 'failed', str(e))
            return False
    
    def _restore_timer_resolution(self) -> None:
        """Restore original timer resolution."""
        try:
            if self._original_timer_resolution:
                ntdll = ctypes.windll.ntdll
                current = ctypes.c_ulong()
                ntdll.NtSetTimerResolution(self._original_timer_resolution, True, ctypes.byref(current))
                self._log_action('timer', 'restore', 'success')
        except Exception as e:
            self._log_action('timer', 'restore', 'failed', str(e))
        self._original_timer_resolution = None
    
    def _log_action(self, action_type: str, target: str, result: str, details: str = "") -> None:
        """Log an optimization action."""
        action = OptimizationAction(
            action_type=action_type,
            target=target,
            result=result,
            details=details
        )
        self._actions_log.append(action)
    
    def get_actions_log(self) -> List[OptimizationAction]:
        """Get the log of all optimization actions."""
        return self._actions_log.copy()
    
    @property
    def is_active(self) -> bool:
        """Check if game mode is active."""
        return self._game_mode_active
