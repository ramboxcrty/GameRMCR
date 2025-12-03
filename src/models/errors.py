"""Error and diagnostic data models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class ErrorLog:
    """Error log entry."""
    timestamp: datetime
    level: str  # ERROR, WARNING, INFO
    context: str
    message: str
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "context": self.context,
            "message": self.message,
            "stack_trace": self.stack_trace
        }
    
    @staticmethod
    def from_dict(data: dict) -> "ErrorLog":
        """Create from dictionary."""
        return ErrorLog(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            level=data["level"],
            context=data["context"],
            message=data["message"],
            stack_trace=data.get("stack_trace")
        )


@dataclass
class InjectionAttempt:
    """DLL injection attempt record."""
    process_name: str
    attempt_number: int
    success: bool
    error_message: Optional[str]
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "process_name": self.process_name,
            "attempt_number": self.attempt_number,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }
    
    @staticmethod
    def from_dict(data: dict) -> "InjectionAttempt":
        """Create from dictionary."""
        return InjectionAttempt(
            process_name=data["process_name"],
            attempt_number=data["attempt_number"],
            success=data["success"],
            error_message=data.get("error_message"),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
