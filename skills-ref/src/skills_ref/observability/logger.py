"""
Structured logging for AgentSkills.
"""

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TextIO

from ..secrets.masking import SecretMasker


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def to_logging_level(self) -> int:
        """Convert to Python logging level."""
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping[self]


@dataclass
class LogEntry:
    """A structured log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    logger_name: str = "agentskills"

    # Context fields (auto-injected)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    skill_name: Optional[str] = None

    # Additional fields
    fields: Dict[str, Any] = field(default_factory=dict)

    # Error information
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_stack: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "timestamp": self.timestamp.isoformat() + "Z",
            "level": self.level.value,
            "message": self.message,
            "logger": self.logger_name,
        }

        # Add context fields if present
        if self.trace_id:
            result["trace_id"] = self.trace_id
        if self.span_id:
            result["span_id"] = self.span_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.workspace_id:
            result["workspace_id"] = self.workspace_id
        if self.skill_name:
            result["skill_name"] = self.skill_name

        # Add extra fields
        if self.fields:
            result["fields"] = self.fields

        # Add error info
        if self.error_type:
            result["error"] = {
                "type": self.error_type,
                "message": self.error_message,
                "stack": self.error_stack,
            }

        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class LogContext:
    """Context for structured logging."""
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    skill_name: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class StructuredLogger:
    """
    Production-grade structured logger.

    Features:
    - JSON output format
    - Automatic secret masking
    - Context injection (user, trace, skill)
    - Field-based logging
    """

    def __init__(
        self,
        name: str = "agentskills",
        level: LogLevel = LogLevel.INFO,
        output: Optional[TextIO] = None,
        masker: Optional[SecretMasker] = None,
        context: Optional[LogContext] = None,
    ):
        self.name = name
        self.level = level
        self.output = output or sys.stdout
        self.masker = masker or SecretMasker()
        self.context = context or LogContext()

    def with_context(self, **kwargs) -> "StructuredLogger":
        """
        Create a new logger with additional context.

        Returns a new logger instance with merged context.
        """
        new_context = LogContext(
            trace_id=kwargs.get("trace_id", self.context.trace_id),
            span_id=kwargs.get("span_id", self.context.span_id),
            user_id=kwargs.get("user_id", self.context.user_id),
            workspace_id=kwargs.get("workspace_id", self.context.workspace_id),
            skill_name=kwargs.get("skill_name", self.context.skill_name),
            extra={**self.context.extra, **kwargs.get("extra", {})},
        )
        return StructuredLogger(
            name=self.name,
            level=self.level,
            output=self.output,
            masker=self.masker,
            context=new_context,
        )

    def debug(self, message: str, **fields) -> None:
        """Log at DEBUG level."""
        self._log(LogLevel.DEBUG, message, fields)

    def info(self, message: str, **fields) -> None:
        """Log at INFO level."""
        self._log(LogLevel.INFO, message, fields)

    def warning(self, message: str, **fields) -> None:
        """Log at WARNING level."""
        self._log(LogLevel.WARNING, message, fields)

    def warn(self, message: str, **fields) -> None:
        """Alias for warning."""
        self.warning(message, **fields)

    def error(self, message: str, error: Optional[Exception] = None, **fields) -> None:
        """Log at ERROR level with optional exception."""
        self._log(LogLevel.ERROR, message, fields, error=error)

    def critical(self, message: str, error: Optional[Exception] = None, **fields) -> None:
        """Log at CRITICAL level with optional exception."""
        self._log(LogLevel.CRITICAL, message, fields, error=error)

    def _log(
        self,
        level: LogLevel,
        message: str,
        fields: Dict[str, Any],
        error: Optional[Exception] = None,
    ) -> None:
        """Internal log method."""
        # Check log level
        if level.to_logging_level() < self.level.to_logging_level():
            return

        # Mask secrets in message and fields
        masked_message = self.masker.mask(message)
        masked_fields = self.masker.mask_dict(fields) if fields else {}

        # Create entry
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=masked_message,
            logger_name=self.name,
            trace_id=self.context.trace_id,
            span_id=self.context.span_id,
            user_id=self.context.user_id,
            workspace_id=self.context.workspace_id,
            skill_name=self.context.skill_name,
            fields={**self.context.extra, **masked_fields},
        )

        # Add error info
        if error:
            import traceback
            entry.error_type = type(error).__name__
            entry.error_message = self.masker.mask(str(error))
            entry.error_stack = self.masker.mask(traceback.format_exc())

        # Output
        self.output.write(entry.to_json() + "\n")
        self.output.flush()


# Module-level logger registry
_loggers: Dict[str, StructuredLogger] = {}
_default_level = LogLevel.INFO
_default_masker = SecretMasker()


def configure_logging(
    level: LogLevel = LogLevel.INFO,
    masker: Optional[SecretMasker] = None,
) -> None:
    """Configure global logging settings."""
    global _default_level, _default_masker
    _default_level = level
    if masker:
        _default_masker = masker


def get_logger(name: str = "agentskills") -> StructuredLogger:
    """
    Get a logger by name.

    Returns existing logger or creates new one.
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(
            name=name,
            level=_default_level,
            masker=_default_masker,
        )
    return _loggers[name]


class LoggingMiddleware:
    """
    Middleware for logging skill execution.

    Automatically logs:
    - Skill start/end
    - Execution duration
    - Success/failure status
    - Error details
    """

    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or get_logger("skill_execution")

    async def before(self, skill_name: str, inputs: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Log before skill execution."""
        self.logger.with_context(skill_name=skill_name).info(
            f"Starting skill: {skill_name}",
            input_keys=list(inputs.keys()),
            user_id=context.get("user_id"),
            trace_id=context.get("trace_id"),
        )

    async def after(
        self,
        skill_name: str,
        result: Any,
        duration_ms: float,
        context: Dict[str, Any],
    ) -> None:
        """Log after successful skill execution."""
        self.logger.with_context(skill_name=skill_name).info(
            f"Completed skill: {skill_name}",
            duration_ms=duration_ms,
            success=True,
            user_id=context.get("user_id"),
            trace_id=context.get("trace_id"),
        )

    async def on_error(
        self,
        skill_name: str,
        error: Exception,
        duration_ms: float,
        context: Dict[str, Any],
    ) -> None:
        """Log skill execution error."""
        self.logger.with_context(skill_name=skill_name).error(
            f"Failed skill: {skill_name}",
            error=error,
            duration_ms=duration_ms,
            success=False,
            user_id=context.get("user_id"),
            trace_id=context.get("trace_id"),
        )
