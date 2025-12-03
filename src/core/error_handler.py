"""Error handler for logging, crash dumps, and blacklist management."""
import json
import traceback
import psutil
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional
import time

from src.models.errors import ErrorLog, InjectionAttempt


class ErrorHandler:
    """Handle errors, crashes, and maintain game blacklist.
    
    Provides comprehensive error logging, injection retry logic,
    blacklist management, and diagnostic export.
    """
    
    def __init__(self, log_dir: Optional[Path] = None, blacklist_file: Optional[Path] = None):
        """Initialize error handler.
        
        Args:
            log_dir: Directory for error logs
            blacklist_file: Path to blacklist JSON file
        """
        self.log_dir = log_dir or Path("logs")
        self.blacklist_file = blacklist_file or Path("config/blacklist.json")
        self.error_logs: List[ErrorLog] = []
        self.injection_attempts: List[InjectionAttempt] = []
        self.blacklist: Set[str] = set()
        
        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.blacklist_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load blacklist
        self.load_blacklist()
    
    def log_error(self, context: str, message: str, level: str = "ERROR", 
                  include_trace: bool = True) -> None:
        """Log an error with timestamp, context, and stack trace.
        
        Args:
            context: Context where error occurred (e.g., "DLL Injection", "Monitoring")
            message: Error message
            level: Error level (ERROR, WARNING, INFO)
            include_trace: Whether to include stack trace
        """
        stack_trace = None
        if include_trace and level == "ERROR":
            stack_trace = traceback.format_exc()
        
        error_log = ErrorLog(
            timestamp=datetime.now(),
            level=level,
            context=context,
            message=message,
            stack_trace=stack_trace
        )
        
        self.error_logs.append(error_log)
        
        # Also write to file immediately
        self._write_error_to_file(error_log)
    
    def _write_error_to_file(self, error_log: ErrorLog) -> None:
        """Write error log to file."""
        log_file = self.log_dir / "errors.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{error_log.timestamp.isoformat()}] {error_log.level} - {error_log.context}\n")
            f.write(f"Message: {error_log.message}\n")
            if error_log.stack_trace:
                f.write(f"Stack Trace:\n{error_log.stack_trace}\n")
            f.write("-" * 80 + "\n")
    
    def log_injection_attempt(self, attempt: InjectionAttempt) -> None:
        """Log a DLL injection attempt.
        
        Args:
            attempt: Injection attempt record
        """
        self.injection_attempts.append(attempt)
        
        # Log as error if failed
        if not attempt.success:
            self.log_error(
                "DLL Injection",
                f"Injection failed for {attempt.process_name} (attempt {attempt.attempt_number}): {attempt.error_message}",
                level="WARNING",
                include_trace=False
            )
    
    def retry_injection_with_backoff(self, process_name: str, 
                                    injection_func, max_retries: int = 3) -> bool:
        """Retry DLL injection with exponential backoff.
        
        Args:
            process_name: Process to inject into
            injection_func: Function to call for injection (should return bool)
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if injection succeeded, False otherwise
        """
        for attempt_num in range(1, max_retries + 1):
            try:
                # Try injection
                success = injection_func()
                
                # Log attempt
                attempt = InjectionAttempt(
                    process_name=process_name,
                    attempt_number=attempt_num,
                    success=success,
                    error_message=None if success else "Injection returned False",
                    timestamp=datetime.now()
                )
                self.log_injection_attempt(attempt)
                
                if success:
                    return True
                
                # Exponential backoff: 1s, 2s, 4s
                if attempt_num < max_retries:
                    delay = 2 ** (attempt_num - 1)
                    time.sleep(delay)
                    
            except Exception as e:
                # Log failed attempt
                attempt = InjectionAttempt(
                    process_name=process_name,
                    attempt_number=attempt_num,
                    success=False,
                    error_message=str(e),
                    timestamp=datetime.now()
                )
                self.log_injection_attempt(attempt)
                
                # Exponential backoff
                if attempt_num < max_retries:
                    delay = 2 ** (attempt_num - 1)
                    time.sleep(delay)
        
        # All attempts failed - add to blacklist
        self.add_to_blacklist(process_name)
        return False
    
    def add_to_blacklist(self, process_name: str) -> None:
        """Add a process to the blacklist.
        
        Args:
            process_name: Process executable name
        """
        self.blacklist.add(process_name)
        self.save_blacklist()
        
        self.log_error(
            "Blacklist",
            f"Added {process_name} to blacklist after repeated failures",
            level="WARNING",
            include_trace=False
        )
    
    def is_blacklisted(self, process_name: str) -> bool:
        """Check if a process is blacklisted.
        
        Args:
            process_name: Process executable name
            
        Returns:
            True if blacklisted
        """
        return process_name in self.blacklist
    
    def remove_from_blacklist(self, process_name: str) -> bool:
        """Remove a process from blacklist.
        
        Args:
            process_name: Process executable name
            
        Returns:
            True if removed, False if not in blacklist
        """
        if process_name in self.blacklist:
            self.blacklist.remove(process_name)
            self.save_blacklist()
            return True
        return False
    
    def save_blacklist(self) -> None:
        """Save blacklist to file."""
        with open(self.blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.blacklist), f, indent=2)
    
    def load_blacklist(self) -> None:
        """Load blacklist from file."""
        if self.blacklist_file.exists():
            try:
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    blacklist_list = json.load(f)
                    self.blacklist = set(blacklist_list)
            except (json.JSONDecodeError, TypeError):
                self.blacklist = set()
    
    def export_diagnostics(self, filepath: Optional[Path] = None) -> Path:
        """Export diagnostic information to file.
        
        Args:
            filepath: Output file path (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            filepath = self.log_dir / f"diagnostics_{timestamp}.json"
        
        # Gather system info
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": psutil.virtual_memory().total // (1024 * 1024),
            "python_version": f"{psutil.version_info}",
        }
        
        # Compile diagnostics
        diagnostics = {
            "system_info": system_info,
            "error_logs": [log.to_dict() for log in self.error_logs[-50:]],  # Last 50 errors
            "injection_attempts": [att.to_dict() for att in self.injection_attempts[-20:]],  # Last 20 attempts
            "blacklist": list(self.blacklist),
            "total_errors": len(self.error_logs),
            "total_injection_attempts": len(self.injection_attempts)
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(diagnostics, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_crash_dump(self) -> Path:
        """Generate a crash dump with current state.
        
        Returns:
            Path to crash dump file
        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        dump_file = self.log_dir / f"crash_dump_{timestamp}.json"
        
        # Gather crash info
        crash_info = {
            "timestamp": datetime.now().isoformat(),
            "last_error": self.error_logs[-1].to_dict() if self.error_logs else None,
            "recent_errors": [log.to_dict() for log in self.error_logs[-10:]],
            "system_state": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
            }
        }
        
        with open(dump_file, 'w', encoding='utf-8') as f:
            json.dump(crash_info, f, indent=2, ensure_ascii=False)
        
        return dump_file
    
    def check_memory_usage(self, threshold_mb: int = 200) -> bool:
        """Check if memory usage exceeds threshold.
        
        Args:
            threshold_mb: Memory threshold in MB
            
        Returns:
            True if threshold exceeded
        """
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            if memory_mb > threshold_mb:
                self.log_error(
                    "Memory Management",
                    f"Memory usage ({memory_mb:.1f} MB) exceeds threshold ({threshold_mb} MB)",
                    level="WARNING",
                    include_trace=False
                )
                return True
            
            return False
        except Exception as e:
            self.log_error("Memory Management", f"Failed to check memory: {e}")
            return False
    
    def clear_old_logs(self, days: int = 7) -> int:
        """Clear error logs older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of logs cleared
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        original_count = len(self.error_logs)
        
        self.error_logs = [
            log for log in self.error_logs
            if log.timestamp.timestamp() > cutoff
        ]
        
        cleared = original_count - len(self.error_logs)
        if cleared > 0:
            self.log_error(
                "Maintenance",
                f"Cleared {cleared} old error logs (older than {days} days)",
                level="INFO",
                include_trace=False
            )
        
        return cleared
    
    def get_error_summary(self) -> dict:
        """Get summary of errors.
        
        Returns:
            Dictionary with error statistics
        """
        if not self.error_logs:
            return {
                "total": 0,
                "by_level": {},
                "by_context": {},
                "recent": []
            }
        
        # Count by level
        by_level = {}
        for log in self.error_logs:
            by_level[log.level] = by_level.get(log.level, 0) + 1
        
        # Count by context
        by_context = {}
        for log in self.error_logs:
            by_context[log.context] = by_context.get(log.context, 0) + 1
        
        return {
            "total": len(self.error_logs),
            "by_level": by_level,
            "by_context": by_context,
            "recent": [log.to_dict() for log in self.error_logs[-5:]]
        }
