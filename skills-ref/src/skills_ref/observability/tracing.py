"""
Distributed tracing for skill execution.
"""

import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class SpanStatus(Enum):
    """Span completion status."""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class TraceContext:
    """Context for distributed tracing."""
    trace_id: str
    parent_span_id: Optional[str] = None

    # Baggage items (propagated across services)
    baggage: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def new(cls) -> "TraceContext":
        """Create new trace context."""
        return cls(trace_id=secrets.token_hex(16))

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional["TraceContext"]:
        """
        Extract trace context from HTTP headers.

        Supports W3C Trace Context format.
        """
        traceparent = headers.get("traceparent", headers.get("Traceparent"))
        if not traceparent:
            return None

        try:
            parts = traceparent.split("-")
            if len(parts) >= 3:
                # Format: version-trace_id-parent_id-flags
                return cls(
                    trace_id=parts[1],
                    parent_span_id=parts[2],
                )
        except Exception:
            pass

        return None

    def to_headers(self, span_id: str) -> Dict[str, str]:
        """
        Convert to HTTP headers for propagation.

        Uses W3C Trace Context format.
        """
        traceparent = f"00-{self.trace_id}-{span_id}-01"
        headers = {"traceparent": traceparent}

        if self.baggage:
            baggage_str = ",".join(f"{k}={v}" for k, v in self.baggage.items())
            headers["baggage"] = baggage_str

        return headers


@dataclass
class SpanEvent:
    """An event within a span."""
    name: str
    timestamp: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """A single span in a trace."""
    span_id: str
    name: str
    trace_id: str
    parent_span_id: Optional[str] = None

    # Timing
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None

    # Status
    status: SpanStatus = SpanStatus.UNSET
    status_message: Optional[str] = None

    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)

    # Events
    events: List[SpanEvent] = field(default_factory=list)

    # Links to other spans
    links: List[str] = field(default_factory=list)

    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return None
        delta = self.end_time - self.start_time
        return delta.total_seconds() * 1000

    @property
    def is_finished(self) -> bool:
        """Check if span is finished."""
        return self.end_time is not None

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, **attributes) -> None:
        """Add an event to the span."""
        self.events.append(SpanEvent(
            name=name,
            timestamp=datetime.utcnow(),
            attributes=attributes,
        ))

    def end(self, status: SpanStatus = SpanStatus.OK, message: Optional[str] = None) -> None:
        """End the span."""
        self.end_time = datetime.utcnow()
        self.status = status
        self.status_message = message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "status_message": self.status_message,
            "attributes": self.attributes,
            "events": [
                {
                    "name": e.name,
                    "timestamp": e.timestamp.isoformat(),
                    "attributes": e.attributes,
                }
                for e in self.events
            ],
        }


class DistributedTracer:
    """
    Distributed tracing for skill execution.

    Features:
    - Trace context propagation
    - Span creation and management
    - Export to various backends
    - OpenTelemetry compatibility
    """

    def __init__(
        self,
        service_name: str = "agentskills",
        on_span_end: Optional[Callable[[Span], None]] = None,
    ):
        self.service_name = service_name
        self._on_span_end = on_span_end
        self._active_spans: Dict[str, Span] = {}

    def create_trace(self, name: str = "root") -> tuple[TraceContext, Span]:
        """
        Create a new trace with root span.

        Returns (context, root_span).
        """
        context = TraceContext.new()
        span = self.start_span(context, name)
        return context, span

    def start_span(
        self,
        context: TraceContext,
        name: str,
        parent_span: Optional[Span] = None,
        **attributes,
    ) -> Span:
        """Start a new span."""
        span_id = secrets.token_hex(8)
        parent_id = parent_span.span_id if parent_span else context.parent_span_id

        span = Span(
            span_id=span_id,
            name=name,
            trace_id=context.trace_id,
            parent_span_id=parent_id,
            attributes={
                "service.name": self.service_name,
                **attributes,
            },
        )

        self._active_spans[span_id] = span
        return span

    def end_span(
        self,
        span: Span,
        status: SpanStatus = SpanStatus.OK,
        message: Optional[str] = None,
    ) -> None:
        """End a span and export it."""
        span.end(status, message)

        # Remove from active
        self._active_spans.pop(span.span_id, None)

        # Export
        if self._on_span_end:
            self._on_span_end(span)

    def get_active_span(self, span_id: str) -> Optional[Span]:
        """Get an active span by ID."""
        return self._active_spans.get(span_id)

    def inject_context(self, span: Span) -> Dict[str, str]:
        """Get headers for context propagation."""
        context = TraceContext(
            trace_id=span.trace_id,
            parent_span_id=span.span_id,
        )
        return context.to_headers(span.span_id)


class TracingMiddleware:
    """
    Middleware for tracing skill execution.

    Creates spans for each skill execution.
    """

    def __init__(self, tracer: DistributedTracer):
        self.tracer = tracer
        self._context: Optional[TraceContext] = None
        self._current_span: Optional[Span] = None

    def set_context(self, context: TraceContext) -> None:
        """Set the trace context."""
        self._context = context

    async def before(
        self,
        skill_name: str,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Span:
        """Start span before skill execution."""
        trace_context = self._context or TraceContext.new()

        span = self.tracer.start_span(
            trace_context,
            f"skill.execute.{skill_name}",
            skill_name=skill_name,
            input_keys=list(inputs.keys()),
            user_id=context.get("user_id"),
        )

        span.add_event("skill.started")
        self._current_span = span

        return span

    async def after(
        self,
        span: Span,
        result: Any,
        context: Dict[str, Any],
    ) -> None:
        """End span after successful execution."""
        span.add_event("skill.completed")
        span.set_attribute("success", True)
        self.tracer.end_span(span, SpanStatus.OK)

    async def on_error(
        self,
        span: Span,
        error: Exception,
        context: Dict[str, Any],
    ) -> None:
        """End span with error."""
        span.add_event(
            "skill.error",
            error_type=type(error).__name__,
            error_message=str(error),
        )
        span.set_attribute("success", False)
        span.set_attribute("error.type", type(error).__name__)
        self.tracer.end_span(span, SpanStatus.ERROR, str(error))


# Span exporter for Jaeger
class JaegerExporter:
    """Export spans to Jaeger."""

    def __init__(self, endpoint: str = "http://localhost:14268/api/traces"):
        self.endpoint = endpoint

    def export(self, span: Span) -> None:
        """Export a span to Jaeger."""
        # In production, use the Jaeger client library
        # This is a simplified example
        import json
        try:
            import urllib.request
            data = json.dumps(span.to_dict()).encode()
            req = urllib.request.Request(
                self.endpoint,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass  # Don't fail on tracing errors


# Span exporter for console (development)
class ConsoleExporter:
    """Export spans to console."""

    def export(self, span: Span) -> None:
        """Print span to console."""
        import json
        print(json.dumps(span.to_dict(), indent=2, default=str))
