---
name: with-cache
description: Wrap a skill with caching to avoid redundant executions. Results are cached by input hash and returned on subsequent calls.
level: 2
operation: READ
type_params:
  - name: A
    description: Input type (used as cache key)
  - name: B
    description: Output type (cached value)
inputs:
  - name: target
    type: Skill<A, B>
    required: true
    description: The skill to wrap with caching
  - name: ttl
    type: duration
    required: false
    default: 1h
    description: Time-to-live for cached entries
  - name: key_fields
    type: string[]
    required: false
    description: Specific input fields to use as cache key (default = all fields)
  - name: cache_errors
    type: boolean
    required: false
    default: false
    description: Whether to cache error responses
  - name: stale_while_revalidate
    type: duration
    required: false
    description: Serve stale content while refreshing in background
outputs:
  - name: result
    type: B
    description: Cached or fresh result
  - name: cache_hit
    type: boolean
    description: Whether result came from cache
  - name: cached_at
    type: datetime
    description: When the cached value was stored
  - name: ttl_remaining
    type: duration
    description: Time until cache entry expires
---

# with-cache

Decorator that adds transparent caching to any skill.

## Functional Signature

```
with-cache :: ∀A B. Skill<A, B> → Skill<A, B>
```

Caching transforms an expensive skill into a memoised version.

## Why This Matters

Many skill invocations are redundant:
- **Repeated queries**: Same search terms
- **Slow APIs**: External services with latency
- **Expensive operations**: LLM calls, complex computations
- **Rate limits**: Avoid unnecessary API consumption

`with-cache` provides:
- **Automatic memoisation**: No manual cache management
- **TTL-based expiry**: Fresh data when needed
- **Input-based keys**: Intelligent cache invalidation
- **Stale-while-revalidate**: Best of both worlds

## Usage Examples

### Basic caching

```yaml
steps:
  - skill: with-cache
    inputs:
      target: company-research
      ttl: 24h
    outputs:
      result: company_data
      cache_hit: from_cache
```

### Cache with specific key fields

```yaml
steps:
  - skill: with-cache
    inputs:
      target: flight-search
      ttl: 15m
      key_fields:
        - origin
        - destination
        - date
      # Ignores: passenger_count, cabin_class (for cache key)
    outputs:
      result: flights
```

### Stale-while-revalidate pattern

```yaml
steps:
  - skill: with-cache
    inputs:
      target: stock-price
      ttl: 5m
      stale_while_revalidate: 1m
      # Returns cached value immediately, refreshes in background
      # if cached value is between 4-5 minutes old
    outputs:
      result: price
```

### Don't cache errors

```yaml
steps:
  - skill: with-cache
    inputs:
      target: unreliable-api
      cache_errors: false  # Default: only cache successes
      ttl: 1h
```

## Cache Key Generation

Default behaviour: Hash all input fields.

```yaml
# These generate different cache keys:
{ company: "Stripe", depth: "full" }
{ company: "Stripe", depth: "basic" }
{ company: "Square", depth: "full" }
```

### Selective key fields

Only use specified fields for cache key:

```yaml
key_fields: [company]
# Now these share a cache entry:
{ company: "Stripe", depth: "full" }
{ company: "Stripe", depth: "basic" }
```

### Key field considerations

Include fields that affect output:
- Query parameters
- Filters
- Version identifiers

Exclude fields that don't affect output:
- Request IDs
- Timestamps
- User preferences (if same underlying data)

## TTL Strategies

| Data Type | Suggested TTL |
|-----------|---------------|
| Company info | 24h-7d |
| Stock prices | 1-5m |
| Weather | 30m-1h |
| Search results | 15m-1h |
| Exchange rates | 1h-4h |
| Static reference data | 7d-30d |

### Dynamic TTL (future)

```yaml
# Planned: TTL based on output
ttl_from_response: "data.cache_control.max_age"
```

## Type Safety

The type checker validates:

1. **Signature preservation**: Cached skill has same type
2. **READ-only constraint**: Cannot cache WRITE operations
3. **Serialisable outputs**: Results must be cacheable

```yaml
# This will fail type checking:
- skill: with-cache
  inputs:
    target: send-email  # operation: WRITE
  # ERROR: Cannot cache WRITE operations (side effects)
```

## Stale-While-Revalidate

Serve stale content while refreshing in background:

```
Time 0: Cache miss → fetch → store (TTL=5m, SWR=1m)
Time 3m: Cache hit → return cached
Time 4m: Cache hit + background refresh starts
Time 4.1m: Cache hit → return cached (refresh ongoing)
Time 4.2m: Refresh complete → cache updated
Time 5m: Cache miss → fetch fresh
```

Benefits:
- Users always get fast responses
- Data stays relatively fresh
- No request waits for refresh

## Cache Invalidation

### Automatic (TTL-based)

Entries expire after TTL. Simple but may serve stale data.

### Manual (event-driven)

For critical updates, invalidate explicitly:

```yaml
# Invalidate when underlying data changes
- skill: invalidate-cache
  inputs:
    target: company-research
    key: { company: "Stripe" }
```

### Hybrid

Short TTL + stale-while-revalidate:

```yaml
ttl: 5m
stale_while_revalidate: 2m
# Guaranteed fresh within 5 minutes
# Typically fresher due to background refresh
```

## Composing with Other Decorators

### Cache after retry

```yaml
# Retry failures, then cache success
- skill: with-cache
  inputs:
    target:
      skill: with-retry
      inputs:
        target: flaky-api
        max_attempts: 3
    ttl: 1h
```

### Cache with timeout

```yaml
# Timeout long-running calls, cache results
- skill: with-cache
  inputs:
    target:
      skill: with-timeout
      inputs:
        target: slow-api
        timeout: 10s
    ttl: 30m
```

## Observability

Track cache effectiveness:

```yaml
outputs:
  cache_hit: ${hit}           # true = from cache
  cached_at: ${cached}        # when stored
  ttl_remaining: ${remaining} # time until expiry
```

Monitor:
- **Hit rate**: % of requests served from cache
- **Stale rate**: % of requests serving expired content
- **Eviction rate**: How often entries are evicted

## When NOT to Cache

| Scenario | Why |
|----------|-----|
| WRITE operations | Side effects must execute |
| User-specific data | Cache key explosion |
| Real-time data | Staleness unacceptable |
| Large payloads | Memory pressure |
| Security-sensitive | Cache timing attacks |

## See Also

- [with-retry](../with-retry/) - Handle transient failures
- [with-timeout](../with-timeout/) - Bound execution time
- [map-skill](../../_combinators/map-skill/) - Process cached results
