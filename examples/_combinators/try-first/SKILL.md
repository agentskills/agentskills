---
name: try-first
description: Try skills in order until one succeeds. Essential for building resilient workflows with fallback strategies.
level: 2
operation: READ
type_params:
  - name: A
    description: Input type
  - name: B
    description: Output type
inputs:
  - name: skills
    type: Skill<A, B>[]
    required: true
    description: Ordered list of skills to try
  - name: input
    type: A
    required: true
    description: Input to pass to each skill
  - name: timeout_per_skill
    type: duration
    required: false
    default: 30s
    description: Maximum time to wait for each skill
outputs:
  - name: result
    type: B
    description: Result from first successful skill
  - name: successful_skill
    type: string
    description: Name of the skill that succeeded
  - name: attempts
    type: AttemptRecord[]
    description: Record of all attempts (for debugging)
  - name: total_time
    type: duration
    description: Total time across all attempts
---

# try-first

Execute skills in order until one succeeds, providing graceful degradation.

## Functional Signature

```
try-first :: ∀A B. (Skill<A, B>[], A) → B
```

Similar to Haskell's `asum` for Alternative:

```haskell
asum :: Alternative f => [f a] -> f a
asum = foldr (<|>) empty
```

## Why This Matters

Real-world systems fail. APIs go down. Rate limits hit. Data is missing.

`try-first` provides:
- **Graceful degradation**: Primary fails → try secondary
- **Multi-source resilience**: Query multiple providers
- **Quality tiers**: Try best source first, fall back to acceptable
- **Transparent failover**: Callers don't see the complexity

## Usage Examples

### Multi-CRM customer lookup

```yaml
steps:
  - skill: try-first
    inputs:
      skills:
        - hubspot-lookup      # Primary CRM
        - salesforce-lookup   # Secondary CRM
        - linkedin-search     # Fallback to public data
        - company-website-scrape  # Last resort
      input: { company: "Acme Corp" }
    outputs:
      result: customer_data
      successful_skill: data_source
```

### Tiered translation quality

```yaml
steps:
  - skill: try-first
    inputs:
      skills:
        - deepl-translate       # Best quality
        - google-translate      # Good quality
        - azure-translate       # Acceptable
        - basic-dictionary      # Minimal fallback
      input: { text: ${text}, target_lang: "ja" }
    outputs:
      result: translation
```

### Geographic data with fallbacks

```yaml
steps:
  - skill: try-first
    inputs:
      skills:
        - google-maps-geocode
        - mapbox-geocode
        - openstreetmap-geocode
        - ip-based-location     # Rough fallback
      input: { address: ${user_address} }
      timeout_per_skill: 5s
    outputs:
      result: coordinates
```

### Progressive content generation

```yaml
steps:
  - skill: try-first
    inputs:
      skills:
        - claude-opus-generate   # Best but expensive/slow
        - claude-sonnet-generate # Good balance
        - claude-haiku-generate  # Fast fallback
      input: { prompt: ${prompt}, max_tokens: 1000 }
    outputs:
      result: generated_content
      successful_skill: model_used
```

## Type Safety

The type checker validates:

1. **Uniform signatures**: All skills must have same `Skill<A, B>` type
2. **Input compatibility**: Input must match skills' input type
3. **Output type**: Result type is `B`

```yaml
# This will fail type checking:
- skill: try-first
  inputs:
    skills:
      - web-search          # Skill<Query, SearchResults>
      - email-search        # Skill<Query, Email[]>  ← different output!
    input: ${query}
  # ERROR: All skills must have same output type
```

## Failure Semantics

| Scenario | Behaviour |
|----------|-----------|
| First skill succeeds | Return immediately, no further attempts |
| Skill throws error | Log error, try next skill |
| Skill times out | Log timeout, try next skill |
| All skills fail | Throw aggregate error with all attempt records |
| Empty skills list | Throw immediately (invalid configuration) |

## Attempt Records

Each attempt is recorded for debugging:

```yaml
attempts:
  - skill: hubspot-lookup
    status: error
    error: "API rate limit exceeded"
    duration: 1.2s

  - skill: salesforce-lookup
    status: timeout
    duration: 30s

  - skill: linkedin-search
    status: success
    duration: 2.3s
```

## Combining with Other Combinators

### With retry per skill

```yaml
- skill: try-first
  inputs:
    skills:
      - skill: with-retry
        inputs:
          target: primary-api
          max_attempts: 2
      - skill: with-retry
        inputs:
          target: secondary-api
          max_attempts: 2
    input: ${request}
```

### With caching

```yaml
- skill: try-first
  inputs:
    skills:
      - skill: with-cache
        inputs:
          target: expensive-api
          ttl: 1h
      - cheaper-fallback-api
    input: ${query}
```

## Design Considerations

### Ordering matters

Put skills in order of:
1. **Preference** (best quality first)
2. **Speed** (fast failures first if quality equal)
3. **Cost** (cheapest fallbacks last)

### Timeouts

Set `timeout_per_skill` based on:
- Expected response time of slowest skill
- Total acceptable latency budget
- `total_budget / num_skills` as starting point

### Idempotency

Ensure all skills are safe to retry:
- READ operations are naturally idempotent
- WRITE operations need careful consideration

## See Also

- [with-retry](../../_decorators/with-retry/) - Retry single skill
- [fan-out](../fan-out/) - Try all in parallel
- [with-timeout](../../_decorators/with-timeout/) - Timeout wrapper
