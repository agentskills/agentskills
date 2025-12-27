# Observability

The AgentSkills observability module provides comprehensive logging, tracing, and audit capabilities.

## Overview

The observability system provides:
- **Structured logging**: JSON-formatted logs with context
- **Distributed tracing**: W3C Trace Context compatible spans
- **Audit logging**: Immutable, hash-chained audit trail
- **Secret masking**: Automatic sensitive data protection

## Structured Logging

### Quick Start

```python
from skills_ref.observability import StructuredLogger, LogLevel

# Create logger
logger = StructuredLogger(
    service_name="my-skill",
    level=LogLevel.INFO,
)

# Log with context
logger.info("Skill executed", {
    "skill_name": "email-send",
    "duration_ms": 150,
    "user_id": "user-123",
})

# Output:
# {"timestamp": "2025-01-15T10:30:00Z", "level": "info",
#  "service": "my-skill", "message": "Skill executed",
#  "skill_name": "email-send", "duration_ms": 150, "user_id": "user-123"}
```

### Log Levels

```python
from skills_ref.observability import LogLevel

logger.debug("Debug details", {...})   # Verbose debugging
logger.info("General info", {...})      # Normal operations
logger.warning("Warning", {...})        # Potential issues
logger.error("Error occurred", {...})   # Errors
logger.critical("Critical!", {...})     # System failures
```

### Contextual Logging

```python
from skills_ref.observability import LogContext

# Create context for a request
context = LogContext(
    trace_id="trace-abc123",
    span_id="span-xyz789",
    user_id="user-456",
    correlation_id="req-000",
)

# Logger includes context in all entries
logger = StructuredLogger(
    service_name="my-skill",
    context=context,
)

# All logs include trace_id, span_id, etc.
logger.info("Processing request")
```

### Logging Middleware

```python
from skills_ref.observability import LoggingMiddleware

middleware = LoggingMiddleware(
    logger=logger,
    log_inputs=True,
    log_outputs=True,
    mask_sensitive=True,
)

# Wrap skill execution
result = await middleware.execute(skill, inputs)

# Automatically logs:
# - Skill start
# - Input data (masked)
# - Output data (masked)
# - Duration
# - Errors
```

## Distributed Tracing

### Quick Start

```python
from skills_ref.observability import DistributedTracer, TraceContext

# Create tracer
tracer = DistributedTracer(
    service_name="my-skill",
    sample_rate=1.0,  # 100% sampling
)

# Start a trace
with tracer.start_span("process-request") as span:
    span.set_attribute("user_id", "user-123")

    # Create child span
    with tracer.start_span("database-query") as child:
        child.set_attribute("query", "SELECT ...")
        # Do work

    span.set_status("ok")
```

### W3C Trace Context

```python
from skills_ref.observability import TraceContext

# Create context from incoming headers
context = TraceContext.from_headers({
    "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
    "tracestate": "vendor=value",
})

print(context.trace_id)   # "0af7651916cd43dd8448eb211c80319c"
print(context.parent_id)  # "b7ad6b7169203331"

# Create outgoing headers
headers = context.to_headers()
```

### Span Operations

```python
with tracer.start_span("skill-execution") as span:
    # Set attributes
    span.set_attribute("skill.name", "email-send")
    span.set_attribute("skill.level", 2)

    # Add events
    span.add_event("email-composed", {"size_bytes": 1024})
    span.add_event("email-sent", {"recipient": "user@example.com"})

    # Set status
    try:
        result = await execute_skill()
        span.set_status("ok")
    except Exception as e:
        span.set_status("error", str(e))
        span.record_exception(e)
        raise
```

### Trace Propagation

```python
# Extract context from incoming request
parent_context = tracer.extract_context(request.headers)

# Create child span
with tracer.start_span("handle-request", parent=parent_context) as span:
    # Inject context for outgoing request
    headers = tracer.inject_context(span.context)
    response = await http_client.post(url, headers=headers)
```

### Exporters

```python
from skills_ref.observability import (
    ConsoleExporter,
    JaegerExporter,
)

# Console exporter (development)
console = ConsoleExporter()

# Jaeger exporter (production)
jaeger = JaegerExporter(
    endpoint="http://jaeger:14268/api/traces",
    service_name="my-skill",
)

tracer = DistributedTracer(
    service_name="my-skill",
    exporter=jaeger,
)
```

## Audit Logging

### Quick Start

```python
from skills_ref.observability import ImmutableAuditLog, AuditEntry, AuditAction

# Create audit log
audit = ImmutableAuditLog(
    service_name="my-skill",
)

# Log an action
entry = await audit.log(
    action=AuditAction.SKILL_EXECUTE,
    actor_id="user-123",
    resource_type="skill",
    resource_id="email-send",
    details={"inputs": {"to": "user@example.com"}},
)

print(entry.entry_id)     # Unique ID
print(entry.hash)         # SHA-256 hash
print(entry.prev_hash)    # Previous entry's hash (chain)
```

### Audit Actions

| Action | Description |
|--------|-------------|
| `SKILL_EXECUTE` | Skill was executed |
| `SKILL_CREATE` | Skill was created |
| `SKILL_UPDATE` | Skill was modified |
| `SKILL_DELETE` | Skill was deleted |
| `SECRET_ACCESS` | Secret was accessed |
| `AUTH_LOGIN` | User authenticated |
| `AUTH_LOGOUT` | User logged out |
| `PERMISSION_GRANT` | Permission was granted |
| `PERMISSION_REVOKE` | Permission was revoked |
| `CONFIG_CHANGE` | Configuration was changed |

### Hash Chain Verification

```python
# Verify audit log integrity
is_valid = await audit.verify_chain()

if not is_valid:
    print("Audit log has been tampered with!")

# Verify specific entry
entry_valid = await audit.verify_entry(entry_id)
```

### Audit Log Builder

```python
from skills_ref.observability import AuditLogBuilder

audit = (
    AuditLogBuilder()
    .with_service_name("my-skill")
    .with_storage(PostgresAuditStorage(connection))
    .with_encryption(True)
    .with_retention_days(90)
    .build()
)
```

### Querying Audit Logs

```python
# Query by actor
entries = await audit.query(
    actor_id="user-123",
    start_time=datetime(2025, 1, 1),
    end_time=datetime(2025, 1, 31),
)

# Query by action
entries = await audit.query(
    action=AuditAction.SKILL_EXECUTE,
    resource_type="skill",
    limit=100,
)

# Query by resource
entries = await audit.query(
    resource_id="email-send",
)
```

## Secret Masking

### Automatic Masking

```python
from skills_ref.observability import StructuredLogger

logger = StructuredLogger(
    service_name="my-skill",
    mask_sensitive=True,
)

# Sensitive fields are automatically masked
logger.info("User login", {
    "user_id": "user-123",
    "password": "secret123",    # Masked to "********"
    "api_key": "sk-abc123",     # Masked to "sk-***"
})
```

### Custom Masking

```python
from skills_ref.observability import SecretMasker

masker = SecretMasker()

# Register specific secrets
masker.register("my-api-key-12345")

# Mask in log messages
message = masker.mask("Using key my-api-key-12345 for auth")
# "Using key ******** for auth"
```

## Configuration

```bash
# Logging
AGENTSKILLS_LOGGING__LEVEL=info
AGENTSKILLS_LOGGING__FORMAT=json
AGENTSKILLS_LOGGING__INCLUDE_CONTEXT=true
AGENTSKILLS_LOGGING__INCLUDE_TRACE_ID=true
AGENTSKILLS_LOGGING__MASK_SENSITIVE=true

# Tracing
AGENTSKILLS_TRACING__ENABLED=true
AGENTSKILLS_TRACING__SERVICE_NAME=agentskills
AGENTSKILLS_TRACING__SAMPLE_RATE=0.1
AGENTSKILLS_TRACING__EXPORTER=jaeger
AGENTSKILLS_TRACING__JAEGER_ENDPOINT=http://jaeger:14268/api/traces

# Audit
AGENTSKILLS_FEATURES__ENABLE_AUDIT_LOGGING=true
```

## Integration Example

```python
from skills_ref.observability import (
    StructuredLogger,
    DistributedTracer,
    ImmutableAuditLog,
    LogContext,
)

# Initialize observability
logger = StructuredLogger(service_name="skill-service")
tracer = DistributedTracer(service_name="skill-service")
audit = ImmutableAuditLog(service_name="skill-service")

async def execute_skill(request):
    # Extract trace context
    parent = tracer.extract_context(request.headers)

    with tracer.start_span("execute-skill", parent=parent) as span:
        # Set up logging context
        log_context = LogContext(
            trace_id=span.trace_id,
            span_id=span.span_id,
            user_id=request.user_id,
        )
        logger.set_context(log_context)

        # Log start
        logger.info("Skill execution started", {
            "skill_name": request.skill_name,
        })

        try:
            # Execute skill
            result = await skill.execute(request.inputs)

            # Log success
            logger.info("Skill execution completed", {
                "skill_name": request.skill_name,
                "duration_ms": span.duration_ms,
            })

            # Audit log
            await audit.log(
                action=AuditAction.SKILL_EXECUTE,
                actor_id=request.user_id,
                resource_type="skill",
                resource_id=request.skill_name,
                status=AuditStatus.SUCCESS,
            )

            span.set_status("ok")
            return result

        except Exception as e:
            # Log error
            logger.error("Skill execution failed", {
                "skill_name": request.skill_name,
                "error": str(e),
            })

            # Audit log
            await audit.log(
                action=AuditAction.SKILL_EXECUTE,
                actor_id=request.user_id,
                resource_type="skill",
                resource_id=request.skill_name,
                status=AuditStatus.FAILURE,
                details={"error": str(e)},
            )

            span.set_status("error", str(e))
            span.record_exception(e)
            raise
```

## Best Practices

1. **Structured over unstructured**: Use JSON logging with fields, not string concatenation
2. **Include context**: Always include trace_id, user_id, correlation_id
3. **Mask by default**: Enable secret masking in all environments
4. **Sample in production**: Use 10-20% sampling for traces in production
5. **Verify audit logs**: Regularly verify audit log integrity
6. **Retain appropriately**: Set retention policies based on compliance requirements
7. **Monitor observability**: Set up alerts on logging/tracing failures
