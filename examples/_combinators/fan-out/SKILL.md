---
name: fan-out
description: Execute multiple skills in parallel on the same input, collecting all results. Essential for multi-source data gathering.
level: 2
operation: READ
type_params:
  - name: A
    description: Input type (shared across all skills)
  - name: B
    description: Output type (must be same for all skills, or use any)
inputs:
  - name: skills
    type: Skill<A, B>[]
    required: true
    description: Skills to execute in parallel
  - name: input
    type: A
    required: true
    description: Input passed to all skills
  - name: fail_strategy
    type: enum[fail_fast, collect_errors, best_effort]
    required: false
    default: best_effort
    description: How to handle individual skill failures
  - name: timeout
    type: duration
    required: false
    default: 60s
    description: Maximum time to wait for all skills
outputs:
  - name: results
    type: B[]
    description: Results from successful skills (order matches input skills)
  - name: errors
    type: ErrorRecord[]
    description: Errors from failed skills
  - name: success_rate
    type: number
    description: Fraction of skills that succeeded (0.0 to 1.0)
---

# fan-out

Execute multiple skills in parallel on the same input, gathering diverse results.

## Functional Signature

```
fan-out :: ∀A B. (Skill<A, B>[], A) → B[]
```

Similar to running functions in parallel and collecting results:

```haskell
fanOut :: [a -> b] -> a -> [b]
fanOut fs x = parMap ($ x) fs
```

## Why This Matters

Many agent tasks require multi-source data:
- **Research**: Query multiple search engines
- **Verification**: Cross-check facts across sources
- **Comparison**: Get prices from multiple vendors
- **Enrichment**: Gather data from various APIs

`fan-out` provides:
- **Parallel execution**: Don't wait sequentially
- **Fault tolerance**: Some sources can fail
- **Unified interface**: Clean abstraction over complexity

## Usage Examples

### Multi-source company research

```yaml
steps:
  - skill: fan-out
    inputs:
      skills:
        - company-news-search
        - financial-data-fetch
        - social-media-scan
        - glassdoor-reviews
        - linkedin-company
      input: { company: "Stripe" }
      fail_strategy: best_effort
    outputs:
      results: all_data
      success_rate: coverage
```

### Cross-reference fact checking

```yaml
steps:
  - skill: fan-out
    inputs:
      skills:
        - wikipedia-lookup
        - britannica-lookup
        - news-archive-search
        - academic-search
      input: { claim: ${claim_to_verify} }
    outputs:
      results: sources

  - skill: synthesize-verification
    inputs:
      sources: ${sources}
    outputs:
      result: verification_report
```

### Price comparison

```yaml
steps:
  - skill: fan-out
    inputs:
      skills:
        - amazon-price-check
        - ebay-price-check
        - walmart-price-check
        - target-price-check
      input: { product_id: ${product} }
      timeout: 10s
    outputs:
      results: prices
      errors: unavailable_sources

  - skill: reduce-skill
    inputs:
      items: ${prices}
      reducer: find-best-deal
      initial: { best: null, savings: 0 }
```

### Parallel LLM queries (ensemble)

```yaml
steps:
  - skill: fan-out
    inputs:
      skills:
        - claude-analyze
        - gpt4-analyze
        - gemini-analyze
      input: { document: ${doc}, question: ${question} }
    outputs:
      results: analyses

  - skill: consensus-merge
    inputs:
      opinions: ${analyses}
    outputs:
      result: ensemble_answer
```

## Type Safety

The type checker validates:

1. **Uniform input type**: All skills must accept input type `A`
2. **Compatible outputs**: Skills should have same output type `B` (or use `any`)
3. **Result ordering**: Results array matches skills array order

```yaml
# Heterogeneous outputs using 'any':
- skill: fan-out
  inputs:
    skills:
      - fetch-news        # Returns NewsArticle[]
      - fetch-financials  # Returns FinancialData
      - fetch-social      # Returns SocialMentions
    input: { company: "Acme" }
  outputs:
    results: heterogeneous_data  # any[]
```

## Failure Strategies

### fail_fast

Stop all skills if any fails:

```yaml
fail_strategy: fail_fast
# Use when: All sources are required for valid result
# Example: Multi-factor authentication (need all factors)
```

### collect_errors

Wait for all, return both successes and failures:

```yaml
fail_strategy: collect_errors
# Use when: Need to report what failed
# Example: Audit trail, debugging, SLA monitoring
```

### best_effort (default)

Return whatever succeeds, ignore failures:

```yaml
fail_strategy: best_effort
# Use when: Partial data is useful
# Example: Research, price comparison, enrichment
```

## Combining with Other Combinators

### Fan-out then reduce

```yaml
# Gather from multiple sources, synthesize into one
steps:
  - skill: fan-out
    inputs:
      skills: [source-a, source-b, source-c]
      input: ${query}
    outputs:
      results: raw_data

  - skill: reduce-skill
    inputs:
      items: ${raw_data}
      reducer: merge-and-dedupe
      initial: { merged: [], seen: {} }
    outputs:
      result: unified_data
```

### Fan-out with retries

```yaml
- skill: fan-out
  inputs:
    skills:
      - skill: with-retry
        inputs: { target: flaky-api-1, max_attempts: 3 }
      - skill: with-retry
        inputs: { target: flaky-api-2, max_attempts: 3 }
    input: ${request}
```

### Nested fan-out (grid search)

```yaml
# For each model, try each prompt variant
- skill: map-skill
  inputs:
    items: ${models}
    processor:
      skill: fan-out
      inputs:
        skills: ${prompt_variants}
  outputs:
    results: grid_results  # model × prompt matrix
```

## Performance Characteristics

| Metric | Behaviour |
|--------|-----------|
| Latency | Max of individual skill latencies (parallel) |
| Throughput | Sum of individual throughputs |
| Resource use | N concurrent connections/processes |
| Memory | All results held until complete |

## Design Considerations

### Timeout strategy

Set based on:
- Slowest expected skill + buffer
- User's patience threshold
- Downstream processing needs

### Result ordering

Results maintain skill order for predictable processing:

```yaml
skills: [a, b, c]
results: [result_a, result_b, result_c]  # Same order
```

### Heterogeneous results

When skills return different types, use discriminated unions:

```yaml
results:
  - type: news
    data: [...]
  - type: financial
    data: {...}
  - type: social
    data: [...]
```

## See Also

- [try-first](../try-first/) - Try until success (not parallel)
- [map-skill](../map-skill/) - Same skill, multiple inputs
- [reduce-skill](../reduce-skill/) - Combine results
