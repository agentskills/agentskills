---
name: with-timeout
description: Wrap a skill with a timeout constraint. Fails fast if the skill doesn't complete within the specified duration.
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
    description: The skill to wrap with timeout
  - name: timeout
    type: duration
    required: true
    description: Maximum time to wait for completion
  - name: on_timeout
    type: enum[error, default, cancel]
    required: false
    default: error
    description: Behaviour when timeout is reached
  - name: default_value
    type: B
    required: false
    description: Value to return on timeout (when on_timeout=default)
outputs:
  - name: result
    type: B
    description: Result from skill (or default on timeout)
  - name: timed_out
    type: boolean
    description: Whether timeout was reached
  - name: elapsed
    type: duration
    description: Actual execution time
---

# with-timeout

Decorator that adds timeout constraints to any skill.

## Functional Signature

```
with-timeout :: ∀A B. (Skill<A, B>, Duration) → Skill<A, B>
```

Ensures bounded execution time for any skill.

## Why This Matters

Unbounded operations are dangerous:
- **Hanging requests**: User waits forever
- **Resource exhaustion**: Connections pile up
- **Cascading failures**: Slow service affects everything
- **Poor UX**: No feedback on progress

`with-timeout` provides:
- **Bounded latency**: Guaranteed maximum wait time
- **Fast failure**: Don't wait for hopeless requests
- **Resource protection**: Free up connections
- **Graceful degradation**: Return defaults or fallback

## Usage Examples

### Basic timeout

```yaml
steps:
  - skill: with-timeout
    inputs:
      target: slow-api-call
      timeout: 10s
    outputs:
      result: response
      timed_out: did_timeout
```

### With default value

```yaml
steps:
  - skill: with-timeout
    inputs:
      target: optional-enrichment
      timeout: 5s
      on_timeout: default
      default_value: { enriched: false, data: null }
    outputs:
      result: enrichment
```

### In a map operation

```yaml
steps:
  - skill: map-skill
    inputs:
      items: ${urls}
      processor:
        skill: with-timeout
        inputs:
          target: fetch-url
          timeout: 30s
          on_timeout: default
          default_value: { status: "timeout", content: null }
```

### Tiered timeouts

```yaml
steps:
  # Fast path: Try quick cache lookup
  - skill: with-timeout
    inputs:
      target: cache-lookup
      timeout: 100ms
      on_timeout: default
      default_value: null
    outputs:
      result: cached

  # Slow path: Only if cache missed
  - skill: conditional
    inputs:
      condition: ${cached == null}
      then:
        skill: with-timeout
        inputs:
          target: full-fetch
          timeout: 30s
```

## Timeout Behaviours

### error (default)

Throw TimeoutError when timeout reached:

```yaml
on_timeout: error
# Raises: TimeoutError after ${timeout}
# Use when: Timeout is exceptional, caller handles error
```

### default

Return specified default value:

```yaml
on_timeout: default
default_value: { status: "unavailable" }
# Returns: default_value after ${timeout}
# Use when: Partial results acceptable, workflow continues
```

### cancel

Attempt to cancel the running operation:

```yaml
on_timeout: cancel
# Sends cancellation signal to skill
# Use when: Skill supports cancellation, avoid resource waste
```

## Setting Timeout Values

### Based on SLA

```yaml
# User-facing: Fast feedback
timeout: 3s

# Background job: More tolerance
timeout: 60s

# Batch processing: Very tolerant
timeout: 5m
```

### Based on dependency

```yaml
# Fast service (cache, local)
timeout: 100ms

# Medium service (database, fast API)
timeout: 5s

# Slow service (LLM, complex computation)
timeout: 60s

# Very slow (batch, export)
timeout: 10m
```

### With retry budget

```yaml
# Total budget = 30s
# With 3 retries, each attempt gets 10s
- skill: with-retry
  inputs:
    target:
      skill: with-timeout
      inputs:
        target: api-call
        timeout: 10s
    max_attempts: 3
```

## Type Safety

The type checker validates:

1. **Signature preservation**: Timeout skill has same type
2. **Default type match**: `default_value` must match output type `B`
3. **Duration validity**: Timeout must be positive duration

```yaml
# This will fail type checking:
- skill: with-timeout
  inputs:
    target: fetch-data        # Returns DataResponse
    timeout: 10s
    on_timeout: default
    default_value: "timeout"  # string, not DataResponse
  # ERROR: default_value type 'string' doesn't match output type 'DataResponse'
```

## Composing with Other Decorators

### Timeout with retry

```yaml
# Each retry attempt has its own timeout
- skill: with-retry
  inputs:
    target:
      skill: with-timeout
      inputs:
        target: slow-api
        timeout: 10s
    max_attempts: 3
    initial_delay: 1s
```

### Timeout with cache

```yaml
# Cache successful results, timeout on fetch
- skill: with-cache
  inputs:
    target:
      skill: with-timeout
      inputs:
        target: slow-lookup
        timeout: 30s
    ttl: 1h
```

### Timeout with fallback

```yaml
# Timeout, then try fallback
- skill: try-first
  inputs:
    skills:
      - skill: with-timeout
        inputs:
          target: primary-api
          timeout: 5s
      - skill: with-timeout
        inputs:
          target: fallback-api
          timeout: 10s  # More patience for fallback
```

## Observability

Track timeout patterns:

```yaml
outputs:
  timed_out: ${timed_out}  # true = hit timeout
  elapsed: ${elapsed}       # actual time taken
```

Monitor:
- **Timeout rate**: % of requests timing out
- **p99 latency**: Are timeouts set appropriately?
- **Elapsed distribution**: How close to timeout?

High timeout rates may indicate:
- Timeout too aggressive
- Dependency degradation
- Need for circuit breaker

## Design Considerations

### Don't timeout too aggressively

```yaml
# Bad: Random failures on normal operations
timeout: 100ms  # Normal p99 is 150ms

# Good: Catch truly stuck requests
timeout: 500ms  # Well above normal p99
```

### Don't timeout too generously

```yaml
# Bad: User waits forever
timeout: 5m  # For a search query

# Good: Fail fast, let user retry
timeout: 10s
```

### Consider downstream timeouts

```yaml
# If calling service A which calls B:
# A's timeout should be > B's timeout + overhead

# Service B: timeout: 5s
# Service A: timeout: 7s (5s + 2s buffer)
```

## See Also

- [with-retry](../with-retry/) - Retry on failure
- [try-first](../../_combinators/try-first/) - Fallback chain
- [with-cache](../with-cache/) - Avoid slow calls
