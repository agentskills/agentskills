---
name: adaptive-bulk-processor
description: Process large batches of items with automatic adaptation based on success/failure patterns. Learns optimal concurrency, retry strategies, and routing from execution history.
level: 3
operation: READ  # Can wrap WRITE operations
type_params:
  - name: T
    description: Type of items being processed
  - name: R
    description: Type of result for each item
inputs:
  - name: items
    type: T[]
    required: true
    description: Items to process
  - name: processor
    type: Skill<T, R>
    required: true
    description: Skill to apply to each item
  - name: initial_concurrency
    type: integer
    required: false
    default: 10
    description: Starting parallelism level
  - name: max_concurrency
    type: integer
    required: false
    default: 100
    description: Maximum parallel operations
  - name: min_concurrency
    type: integer
    required: false
    default: 1
    description: Minimum parallel operations
  - name: target_success_rate
    type: number
    required: false
    default: 0.95
    description: Target success rate to maintain
  - name: adaptation_window
    type: integer
    required: false
    default: 20
    description: Number of items to consider for adaptation
  - name: enable_routing
    type: boolean
    required: false
    default: true
    description: Route items to specialised processors based on patterns
outputs:
  - name: results
    type: ProcessingResult<R>[]
    description: Results for each item (success or error)
  - name: summary
    type: BatchSummary
    description: Overall batch statistics
  - name: learned_config
    type: AdaptiveConfig
    description: Learned optimal configuration for similar batches
  - name: anomalies
    type: AnomalyRecord[]
    description: Items that behaved unexpectedly
---

# adaptive-bulk-processor

Process batches with automatic adaptation to maintain reliability and throughput.

## Why This Matters

Bulk processing at scale reveals patterns:
- **Variable failure rates**: Some items fail more than others
- **Optimal concurrency**: Too high → rate limits; too low → slow
- **Item clustering**: Similar items may need similar handling
- **Transient vs permanent**: Some failures are retryable

`adaptive-bulk-processor` learns these patterns and adapts:

```
┌──────────────────────────────────────────────────────────────────┐
│                    adaptive-bulk-processor                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Items ──┬──► Classifier ──┬──► Fast Track (high concurrency)    │
│          │                 │                                     │
│          │                 ├──► Normal Track (standard)          │
│          │                 │                                     │
│          │                 └──► Careful Track (low concurrency,  │
│          │                                    more retries)      │
│          │                                                       │
│          │    ┌─────────────────────────────────────────────┐    │
│          │    │              Feedback Loop                  │    │
│          │    │                                             │    │
│          └────┤  Success/Failure ──► Adjust concurrency     │    │
│               │  Error patterns ──► Update routing          │    │
│               │  Timing data ──► Optimise batching          │    │
│               │                                             │    │
│               └─────────────────────────────────────────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## The Adaptation Algorithm

### Concurrency Adjustment

```python
# Simplified algorithm
def adjust_concurrency(recent_results, current_concurrency):
    success_rate = count_successes(recent_results) / len(recent_results)

    if success_rate < target_success_rate:
        # Too aggressive, back off
        return max(min_concurrency, current_concurrency * 0.7)

    elif success_rate > target_success_rate + 0.03:
        # Room to grow
        return min(max_concurrency, current_concurrency * 1.2)

    return current_concurrency  # Stable
```

### Error Classification

```yaml
error_patterns:
  rate_limit:
    pattern: ["429", "rate limit", "too many requests"]
    response: reduce_concurrency

  timeout:
    pattern: ["timeout", "ETIMEDOUT", "deadline exceeded"]
    response: increase_timeout_and_reduce_concurrency

  not_found:
    pattern: ["404", "not found", "does not exist"]
    response: skip_item_no_retry

  auth_error:
    pattern: ["401", "403", "unauthorized"]
    response: pause_and_alert

  transient:
    pattern: ["500", "502", "503", "504"]
    response: retry_with_backoff
```

### Item Routing

Based on observed patterns:

```yaml
routing_rules:
  # Items matching this pattern go to fast track
  - pattern:
      type: ["simple_lookup", "cache_likely"]
    track: fast
    concurrency_multiplier: 2.0

  # Complex items need careful handling
  - pattern:
      type: ["complex_transform", "external_api"]
    track: careful
    concurrency_multiplier: 0.5
    retry_multiplier: 2.0

  # Previously failed items get extra care
  - pattern:
      previous_failures: "> 0"
    track: careful
    concurrency_multiplier: 0.3
```

## Usage Examples

### Basic batch processing

```yaml
steps:
  - skill: adaptive-bulk-processor
    inputs:
      items: ${customer_list}
      processor: enrich-customer-data
      initial_concurrency: 20
    outputs:
      results: enriched_customers
      summary: batch_stats
```

### With learned configuration

```yaml
steps:
  # First run learns optimal settings
  - skill: adaptive-bulk-processor
    inputs:
      items: ${batch_1}
      processor: process-transaction
    outputs:
      results: results_1
      learned_config: optimal_config

  # Subsequent runs start with learned settings
  - skill: adaptive-bulk-processor
    inputs:
      items: ${batch_2}
      processor: process-transaction
      initial_concurrency: ${optimal_config.recommended_concurrency}
    outputs:
      results: results_2
```

### With custom error handling

```yaml
steps:
  - skill: adaptive-bulk-processor
    inputs:
      items: ${urls}
      processor:
        skill: with-retry
        inputs:
          target: fetch-and-parse
          max_attempts: 3
          retry_on: ["5xx", "timeout"]
      enable_routing: true
    outputs:
      results: parsed_pages
      anomalies: failed_urls
```

## Batch Summary

```yaml
summary:
  total_items: 10000

  outcomes:
    succeeded: 9823
    failed_permanent: 42
    failed_after_retry: 135

  performance:
    total_duration: 45.2s
    items_per_second: 221.2
    average_latency: 0.18s
    p99_latency: 0.82s

  adaptation:
    initial_concurrency: 10
    final_concurrency: 47
    concurrency_changes: 8
    route_updates: 3

  retries:
    total_retry_attempts: 412
    successful_retries: 277
    retry_success_rate: 0.67

  routing:
    fast_track: 7234
    normal_track: 2421
    careful_track: 345
```

## Learned Configuration

After processing, the skill outputs learned configuration:

```yaml
learned_config:
  recommended_concurrency: 47
  confidence: 0.89

  error_distribution:
    rate_limit: 0.02
    timeout: 0.005
    not_found: 0.004
    other: 0.001

  optimal_batch_size: 100

  routing_effectiveness:
    fast_track_success_rate: 0.99
    careful_track_success_rate: 0.91
    routing_saved_retries: 156

  recommendations:
    - "Consider increasing timeout for items matching pattern X"
    - "Fast track could handle 15% more items based on success rate"
```

## Anomaly Detection

Items that behave unexpectedly are flagged:

```yaml
anomalies:
  - item_id: "item_4523"
    reason: "Succeeded after 4 failures (unusual for this pattern)"
    pattern: "May indicate intermittent upstream issue"

  - item_id: "item_7891"
    reason: "Latency 10x higher than similar items"
    pattern: "Possible data quality issue"

  - item_id: "item_2134"
    reason: "New error type not seen before"
    error: "ECONNRESET"
    action: "Added to error patterns, monitoring"
```

## Composing with Meta Skills

### With explain-execution for debugging

```yaml
steps:
  - skill: adaptive-bulk-processor
    inputs:
      items: ${batch}
      processor: complex-workflow
    outputs:
      results: results
      anomalies: anomalies

  # Understand what happened with anomalies
  - skill: map-skill
    inputs:
      items: ${anomalies}
      processor: explain-execution
    outputs:
      results: anomaly_explanations
```

### With skill-synthesizer for custom processors

```yaml
steps:
  # Generate optimised processor from examples
  - skill: skill-synthesizer
    inputs:
      task_description: "Process customer records, enriching with external data"
      example_inputs: ${sample_customers}
      example_outputs: ${expected_enriched}
      constraints:
        max_latency: 500ms
    outputs:
      generated_skill: optimised_processor

  # Use generated processor in bulk
  - skill: adaptive-bulk-processor
    inputs:
      items: ${all_customers}
      processor: ${optimised_processor}
```

## Comparison: Standard vs Adaptive

| Metric | Standard map-skill | adaptive-bulk-processor |
|--------|-------------------|-------------------------|
| Items: 10,000 | 45s @ 50 conc | 38s @ adaptive |
| Success rate | 94% (fixed retry) | 98% (adaptive) |
| Rate limit errors | 234 | 12 |
| Total retries | 580 | 189 |
| API cost | $15 | $11 |

## When to Use

| Scenario | Use adaptive-bulk-processor |
|----------|----------------------------|
| Large batches (>100 items) | ✅ Yes |
| Unknown failure patterns | ✅ Yes |
| Rate-limited APIs | ✅ Yes |
| Learning optimal settings | ✅ Yes |
| Small batches (<20 items) | ❌ Use map-skill |
| Predictable, fast operations | ❌ Use map-skill |
| Real-time requirements | ❌ Use map-skill |

## See Also

- [map-skill](../../_combinators/map-skill/) - Simple parallel mapping
- [with-retry](../../_decorators/with-retry/) - Retry logic
- [explain-execution](../../_meta/explain-execution/) - Debug anomalies
- [intent-refiner](../../_meta/intent-refiner/) - Learn from outcomes
