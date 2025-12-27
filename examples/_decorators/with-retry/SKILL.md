---
name: with-retry
description: Wrap a skill with automatic retry logic and exponential backoff. Essential for resilient workflows with unreliable dependencies.
level: 2
operation: READ
type_params:
  - name: A
    description: Input type (preserved from wrapped skill)
  - name: B
    description: Output type (preserved from wrapped skill)
inputs:
  - name: target
    type: Skill<A, B>
    required: true
    description: The skill to wrap with retry logic
  - name: max_attempts
    type: integer
    required: false
    default: 3
    description: Maximum number of attempts (including first try)
  - name: backoff
    type: enum[constant, linear, exponential]
    required: false
    default: exponential
    description: Backoff strategy between retries
  - name: initial_delay
    type: duration
    required: false
    default: 1s
    description: Delay before first retry
  - name: max_delay
    type: duration
    required: false
    default: 30s
    description: Maximum delay between retries
  - name: retry_on
    type: string[]
    required: false
    default: ["*"]
    description: Error types to retry on (* = all errors)
  - name: jitter
    type: boolean
    required: false
    default: true
    description: Add randomness to delays to avoid thundering herd
outputs:
  - name: result
    type: B
    description: Result from successful attempt
  - name: attempts
    type: integer
    description: Number of attempts made
  - name: total_delay
    type: duration
    description: Total time spent in backoff delays
  - name: errors
    type: ErrorRecord[]
    description: Errors from failed attempts
---

# with-retry

Decorator that adds automatic retry logic to any skill.

## Functional Signature

```
with-retry :: ∀A B. Skill<A, B> → Skill<A, B>
```

This is a **skill transformer**: it takes a skill and returns an enhanced version.

## Why This Matters

Real-world systems are unreliable:
- **Network errors**: Temporary connectivity issues
- **Rate limits**: API throttling
- **Transient failures**: Temporary service unavailability
- **Timeouts**: Slow responses under load

`with-retry` provides:
- **Automatic recovery**: No manual retry loops
- **Backoff strategies**: Avoid hammering failing services
- **Jitter**: Prevent thundering herd
- **Observability**: Track retry patterns

## Usage Examples

### Basic retry

```yaml
steps:
  - skill: with-retry
    inputs:
      target: flaky-api-call
      max_attempts: 3
    outputs:
      result: api_response
      attempts: retry_count
```

### With exponential backoff

```yaml
steps:
  - skill: with-retry
    inputs:
      target: rate-limited-api
      max_attempts: 5
      backoff: exponential
      initial_delay: 2s
      max_delay: 60s
    outputs:
      result: response
```

### Retry only specific errors

```yaml
steps:
  - skill: with-retry
    inputs:
      target: database-query
      retry_on:
        - "ConnectionError"
        - "TimeoutError"
        - "503"
      max_attempts: 3
    outputs:
      result: query_result
```

### Inline in workflow

```yaml
steps:
  - skill: map-skill
    inputs:
      items: ${urls}
      processor:
        skill: with-retry
        inputs:
          target: fetch-url
          max_attempts: 2
          initial_delay: 500ms
```

## Backoff Strategies

### Constant

Same delay between each retry:

```
Attempt 1 → fail → wait 1s → Attempt 2 → fail → wait 1s → Attempt 3
```

Use when: Failures are truly random, service has no rate limiting.

### Linear

Delay increases by fixed amount:

```
Attempt 1 → fail → wait 1s → Attempt 2 → fail → wait 2s → Attempt 3 → fail → wait 3s
```

Use when: Gradual backoff needed, moderate rate limiting.

### Exponential (default)

Delay doubles each time:

```
Attempt 1 → fail → wait 1s → Attempt 2 → fail → wait 2s → Attempt 3 → fail → wait 4s
```

Use when: Rate limiting, resource contention, cascading failures.

### With jitter

Random variation prevents synchronized retries:

```
Attempt 1 → fail → wait 1.2s → Attempt 2 → fail → wait 1.8s → ...
```

Use when: Multiple clients might retry simultaneously.

## Type Safety

The type checker validates:

1. **Signature preservation**: Output skill has same type as input skill
2. **Operation preservation**: READ skill stays READ, WRITE stays WRITE
3. **Input/output types**: Unchanged through decoration

```yaml
# Original skill
web-search: Skill<Query, SearchResults>

# After decoration
with-retry(web-search): Skill<Query, SearchResults>  # Same signature
```

## Error Handling

### Retriable errors (default)

All errors trigger retry unless filtered:

```yaml
retry_on: ["*"]  # Retry everything
```

### Filtered errors

Only retry specific errors:

```yaml
retry_on:
  - "RateLimitError"
  - "TimeoutError"
  - "5xx"  # Any 5xx HTTP status
```

### Non-retriable errors

Some errors should fail immediately:

```yaml
# These should NOT be retried:
# - AuthenticationError (creds are wrong)
# - ValidationError (input is invalid)
# - NotFoundError (resource doesn't exist)
```

## Composing Decorators

Decorators can be stacked:

```yaml
# Retry, then cache successful results
- skill: with-cache
  inputs:
    target:
      skill: with-retry
      inputs:
        target: expensive-api
        max_attempts: 3
    ttl: 1h
```

Order matters:
- `with-cache(with-retry(x))`: Cache retried results
- `with-retry(with-cache(x))`: Retry cache misses (usually wrong)

## Observability

Track retry patterns for operational insights:

```yaml
outputs:
  attempts: ${attempts}     # 3 = two retries
  total_delay: ${delay}     # 7s = 1s + 2s + 4s backoff
  errors: ${errors}         # List of what went wrong
```

High retry counts may indicate:
- Unhealthy dependencies
- Need for circuit breaker
- Capacity issues

## When NOT to Retry

| Scenario | Why |
|----------|-----|
| WRITE operations | May cause duplicates |
| Non-idempotent actions | Side effects repeat |
| Authentication failures | Creds won't magically fix |
| Validation errors | Input needs fixing |
| Business logic errors | Not transient |

## Related Patterns

### Circuit Breaker

For systemic failures, use circuit breaker instead:

```yaml
# After N failures, stop trying for a period
- skill: with-circuit-breaker
  inputs:
    target: unreliable-service
    failure_threshold: 5
    recovery_timeout: 60s
```

### Fallback

For graceful degradation:

```yaml
- skill: try-first
  inputs:
    skills:
      - skill: with-retry
        inputs: { target: primary-api, max_attempts: 3 }
      - fallback-api
```

## See Also

- [try-first](../../_combinators/try-first/) - Multiple fallback skills
- [with-timeout](../with-timeout/) - Bound execution time
- [with-cache](../with-cache/) - Avoid repeated calls
