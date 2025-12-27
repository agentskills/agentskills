---
name: with-logging
description: Wrap a skill with comprehensive logging of inputs, outputs, timing, and errors. Essential for debugging and observability.
level: 2
operation: READ
type_params:
  - name: A
    description: Input type (preserved)
  - name: B
    description: Output type (preserved)
inputs:
  - name: target
    type: Skill<A, B>
    required: true
    description: The skill to wrap with logging
  - name: log_level
    type: enum[debug, info, warn, error]
    required: false
    default: info
    description: Minimum log level to emit
  - name: log_inputs
    type: boolean
    required: false
    default: true
    description: Whether to log input values
  - name: log_outputs
    type: boolean
    required: false
    default: true
    description: Whether to log output values
  - name: redact_fields
    type: string[]
    required: false
    description: Field names to redact from logs (e.g., passwords, tokens)
  - name: sample_rate
    type: number
    required: false
    default: 1.0
    description: Fraction of invocations to log (0.0 to 1.0)
  - name: include_trace_id
    type: boolean
    required: false
    default: true
    description: Include distributed trace ID in logs
outputs:
  - name: result
    type: B
    description: Result from wrapped skill (unchanged)
  - name: log_entry
    type: LogEntry
    description: The generated log entry
  - name: trace_id
    type: string
    description: Trace ID for correlation
---

# with-logging

Decorator that adds structured logging to any skill for observability.

## Functional Signature

```
with-logging :: ∀A B. Skill<A, B> → Skill<A, B>
```

Transparent logging wrapper that doesn't affect skill behaviour.

## Why This Matters

Complex agent workflows need observability:
- **Debugging**: What happened? What was the input?
- **Performance**: Where is time spent?
- **Auditing**: Who called what, when?
- **Monitoring**: Are skills healthy?
- **Tracing**: Follow requests across skills

`with-logging` provides:
- **Structured logs**: Machine-parseable format
- **Automatic timing**: Duration tracking
- **Error capture**: Full error context
- **Redaction**: Protect sensitive data
- **Sampling**: Control log volume

## Usage Examples

### Basic logging

```yaml
steps:
  - skill: with-logging
    inputs:
      target: customer-lookup
    outputs:
      result: customer
      trace_id: request_trace
```

Generated log:
```json
{
  "skill": "customer-lookup",
  "trace_id": "abc-123",
  "timestamp": "2024-03-15T10:30:00Z",
  "duration_ms": 234,
  "status": "success",
  "inputs": { "customer_id": "cust_001" },
  "outputs": { "name": "Acme Corp", "tier": "enterprise" }
}
```

### With redaction

```yaml
steps:
  - skill: with-logging
    inputs:
      target: authenticate-user
      redact_fields:
        - password
        - token
        - api_key
        - ssn
```

Log output:
```json
{
  "inputs": {
    "username": "alice",
    "password": "[REDACTED]",
    "api_key": "[REDACTED]"
  }
}
```

### Sampled logging (high volume)

```yaml
steps:
  - skill: with-logging
    inputs:
      target: process-event
      sample_rate: 0.01  # Log 1% of invocations
      log_level: debug
```

### Debug-level for development

```yaml
steps:
  - skill: with-logging
    inputs:
      target: complex-workflow
      log_level: debug
      log_inputs: true
      log_outputs: true
```

### Production (minimal)

```yaml
steps:
  - skill: with-logging
    inputs:
      target: api-handler
      log_level: warn  # Only log warnings and errors
      log_outputs: false  # Don't log potentially large outputs
```

## Log Entry Structure

```typescript
interface LogEntry {
  // Identity
  skill: string;
  trace_id: string;
  span_id: string;
  parent_span_id?: string;

  // Timing
  timestamp: datetime;
  duration_ms: number;

  // Status
  status: "success" | "error";
  error?: {
    type: string;
    message: string;
    stack?: string;
  };

  // Data (if enabled)
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;

  // Context
  metadata?: Record<string, any>;
}
```

## Distributed Tracing

When `include_trace_id: true`, logs include correlation IDs:

```yaml
# Parent workflow
- skill: with-logging
  inputs:
    target: research-workflow
  outputs:
    trace_id: parent_trace  # "trace-abc"

# Child skill (automatically inherits trace)
# Logs will show:
# { "trace_id": "trace-abc", "parent_span_id": "span-123", ... }
```

This enables:
- Following requests across skills
- Building execution timelines
- Identifying slow paths

## Redaction Patterns

### Field-based redaction

```yaml
redact_fields:
  - password
  - secret
  - token
  - api_key
  - authorization
```

### Pattern-based redaction (future)

```yaml
redact_patterns:
  - regex: "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"
    replacement: "[EMAIL]"
  - regex: "\\b\\d{3}-\\d{2}-\\d{4}\\b"
    replacement: "[SSN]"
```

## Type Safety

The type checker validates:

1. **Signature preservation**: Logged skill has same type
2. **No behaviour change**: Result is identical
3. **Redact fields exist**: Warning if field doesn't exist in input

## Composing with Other Decorators

### Log retries

```yaml
- skill: with-logging
  inputs:
    target:
      skill: with-retry
      inputs:
        target: flaky-api
        max_attempts: 3
    log_level: info
# Logs each attempt, including failures
```

### Log around cache

```yaml
- skill: with-logging
  inputs:
    target:
      skill: with-cache
      inputs:
        target: expensive-lookup
        ttl: 1h
# Logs cache hits/misses
```

### Full observability stack

```yaml
- skill: with-logging
  inputs:
    target:
      skill: with-retry
      inputs:
        target:
          skill: with-timeout
          inputs:
            target:
              skill: with-cache
              inputs:
                target: api-call
                ttl: 30m
            timeout: 10s
        max_attempts: 3
# Logs: cache hit/miss, timeout, retry attempts, final result
```

## Observability Integration

### Log aggregation

Logs can be shipped to:
- Elasticsearch / OpenSearch
- Datadog
- Splunk
- CloudWatch Logs

### Metrics derivation

From logs, derive:
- Invocation count by skill
- Error rate by skill
- Latency percentiles
- Cache hit ratio

### Alerting

Alert on:
- Error rate > threshold
- Latency p99 > SLA
- Specific error types

## Performance Considerations

| Setting | Impact |
|---------|--------|
| `log_inputs: true` | Serialisation overhead |
| `log_outputs: true` | Serialisation overhead |
| `sample_rate: 0.01` | 99% reduction in log volume |
| `log_level: error` | Only log failures |

For high-throughput skills:
```yaml
sample_rate: 0.001  # 0.1% sampling
log_inputs: false   # Skip input serialisation
log_outputs: false  # Skip output serialisation
```

## See Also

- [explain-execution](../../_meta/explain-execution/) - Reconstruct from logs
- [with-retry](../with-retry/) - Retry with logging
- [with-timeout](../with-timeout/) - Timeout with logging
