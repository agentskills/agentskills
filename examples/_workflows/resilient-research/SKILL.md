---
name: resilient-research
description: Production-grade research workflow demonstrating composition of higher-order skills. Combines caching, retry, parallel execution, and fallbacks for maximum reliability.
level: 3
operation: READ
inputs:
  - name: query
    type: string
    required: true
    description: Research question or topic
  - name: depth
    type: enum[quick, standard, deep]
    required: false
    default: standard
    description: How thoroughly to research
  - name: sources
    type: string[]
    required: false
    default: ["web", "academic", "news"]
    description: Which sources to query
  - name: max_results_per_source
    type: integer
    required: false
    default: 5
    description: Maximum results from each source
  - name: freshness
    type: enum[any, day, week, month, year]
    required: false
    default: any
    description: How recent results should be
outputs:
  - name: synthesis
    type: string
    requires_rationale: true
    description: Synthesised answer to the research query
  - name: sources_used
    type: SourceRecord[]
    requires_source: true
    description: All sources that contributed to the synthesis
  - name: confidence
    type: number
    range: [0, 1]
    description: Confidence in the synthesis based on source agreement
  - name: gaps
    type: string[]
    description: Areas where more research would be valuable
  - name: execution_stats
    type: ExecutionStats
    description: Performance metrics (cache hits, retries, fallbacks used)
---

# resilient-research

A production-grade research workflow that showcases higher-order skill composition.

## Why This Matters

Research is inherently unreliable:
- **APIs fail**: Rate limits, timeouts, server errors
- **Sources disagree**: Conflicting information
- **Latency varies**: 100ms to 10s for different sources
- **Cost adds up**: Each API call costs money

`resilient-research` composes higher-order skills to handle all of this:

```
┌─────────────────────────────────────────────────────────────────┐
│                     resilient-research                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                                │
│  │  with-cache │  ← Cache entire workflow results               │
│  └──────┬──────┘                                                │
│         │                                                       │
│  ┌──────▼──────┐                                                │
│  │   fan-out   │  ← Query all sources in parallel               │
│  └──────┬──────┘                                                │
│         │                                                       │
│    ┌────┴────┬────────┬────────┐                                │
│    │         │        │        │                                │
│  ┌─▼─┐    ┌──▼──┐  ┌──▼──┐  ┌──▼──┐                             │
│  │web│    │acad │  │news │  │...  │  ← Each source skill        │
│  └─┬─┘    └──┬──┘  └──┬──┘  └──┬──┘                             │
│    │         │        │        │                                │
│  ┌─▼─────────▼────────▼────────▼─┐                              │
│  │         with-retry            │  ← Each wrapped with retry   │
│  └─┬─────────┬────────┬────────┬─┘                              │
│    │         │        │        │                                │
│  ┌─▼─────────▼────────▼────────▼─┐                              │
│  │         try-first             │  ← Fallback within category  │
│  └───────────────┬───────────────┘                              │
│                  │                                              │
│  ┌───────────────▼───────────────┐                              │
│  │        reduce-skill           │  ← Merge & synthesise        │
│  └───────────────────────────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation

```yaml
---
name: resilient-research
composes:
  - with-cache
  - fan-out
  - try-first
  - with-retry
  - reduce-skill
  - web-search
  - academic-search
  - news-search
---

steps:
  # Wrap entire workflow with caching
  - skill: with-cache
    inputs:
      target: ${research_workflow}
      ttl: 1h
      key_fields: ["query", "depth", "freshness"]
    outputs:
      result: final_result

  # Define the research workflow
  - define: research_workflow
    steps:
      # Fan out to all sources in parallel
      - skill: fan-out
        inputs:
          input: ${query}
          skills: ${source_skills}
          fail_strategy: best_effort  # Continue even if some fail
          timeout: 30s
        outputs:
          results: raw_results
          stats: source_stats

      # Merge and synthesise results
      - skill: reduce-skill
        inputs:
          items: ${raw_results}
          initial:
            synthesis: ""
            sources: []
            agreements: 0
            contradictions: 0
          reducer: synthesise-findings
        outputs:
          result: merged

      # Calculate confidence from agreement
      - skill: calculate-confidence
        inputs:
          agreements: ${merged.agreements}
          contradictions: ${merged.contradictions}
          source_count: ${raw_results.length}
        outputs:
          confidence: confidence_score

      # Identify gaps
      - skill: identify-research-gaps
        inputs:
          query: ${query}
          findings: ${merged.synthesis}
          sources_queried: ${sources}
          sources_succeeded: ${source_stats.succeeded}
        outputs:
          gaps: knowledge_gaps

  # Build source skills with retry + fallback
  - define: source_skills
    value:
      - skill: try-first
        inputs:
          skills:
            - skill: with-retry
              inputs:
                target: google-search
                max_attempts: 3
            - skill: with-retry
              inputs:
                target: bing-search
                max_attempts: 2
            - skill: with-retry
              inputs:
                target: duckduckgo-search
                max_attempts: 2

      - skill: try-first
        inputs:
          skills:
            - skill: with-retry
              inputs:
                target: semantic-scholar-search
                max_attempts: 3
            - skill: with-retry
              inputs:
                target: arxiv-search
                max_attempts: 2
            - skill: with-retry
              inputs:
                target: google-scholar-search
                max_attempts: 2

      - skill: try-first
        inputs:
          skills:
            - skill: with-retry
              inputs:
                target: newsapi-search
                max_attempts: 3
            - skill: with-retry
              inputs:
                target: google-news-search
                max_attempts: 2
```

## Execution Stats

The workflow tracks comprehensive metrics:

```yaml
execution_stats:
  total_duration: 4.2s

  cache:
    hit: false
    would_save: 4.2s

  sources:
    attempted: 3
    succeeded: 3
    failed: 0

  retries:
    total_attempts: 5
    retries_needed: 2
    sources_retried: ["newsapi-search"]

  fallbacks:
    used: 1
    details:
      - primary: google-scholar-search
        fell_back_to: arxiv-search
        reason: "Rate limit exceeded"

  parallelism:
    parallel_calls: 3
    time_saved_vs_sequential: 8.1s
```

## Confidence Calculation

Confidence is computed from source agreement:

```yaml
# High confidence: Sources agree
confidence: 0.92
evidence:
  - "3/3 sources confirm funding round"
  - "Amounts match within 5%"
  - "Dates consistent"

# Medium confidence: Partial agreement
confidence: 0.65
evidence:
  - "2/3 sources confirm"
  - "1 source has conflicting date"

# Low confidence: Disagreement or single source
confidence: 0.35
evidence:
  - "Only 1 source found"
  - "Web and academic sources contradict"
```

## Depth Levels

| Depth | Sources | Max Results | Timeout | Use Case |
|-------|---------|-------------|---------|----------|
| `quick` | 1 (web only) | 3 | 10s | Quick fact check |
| `standard` | 3 (web, academic, news) | 5 | 30s | General research |
| `deep` | 5+ (all available) | 10 | 60s | Comprehensive analysis |

## Usage Examples

### Quick fact check

```yaml
steps:
  - skill: resilient-research
    inputs:
      query: "What is the current population of Tokyo?"
      depth: quick
      freshness: year
    outputs:
      synthesis: answer
      confidence: certainty
```

### Comprehensive research

```yaml
steps:
  - skill: resilient-research
    inputs:
      query: "Impact of LLMs on software development productivity"
      depth: deep
      sources: ["web", "academic", "news", "arxiv", "github"]
      freshness: month
    outputs:
      synthesis: analysis
      sources_used: references
      gaps: future_research
```

### With intent refinement

```yaml
steps:
  - skill: resilient-research
    inputs:
      query: ${user_query}
    outputs:
      synthesis: initial_answer

  # If user modifies, learn and improve
  - skill: intent-refiner
    inputs:
      original_request: ${user_query}
      execution_result: ${initial_answer}
      user_action: ${user_response}
    outputs:
      learned_preferences: research_prefs

  # Next research uses learned preferences
  - skill: resilient-research
    inputs:
      query: ${next_query}
      depth: ${research_prefs.preferred_depth}
      sources: ${research_prefs.preferred_sources}
```

## Error Handling

The workflow degrades gracefully:

| Scenario | Behaviour |
|----------|-----------|
| All sources for category fail | Return partial results, note gap |
| One source slow | Continue with faster sources |
| Rate limit hit | Retry with backoff, then fallback |
| Network error | Retry, then fallback to cached if available |
| All sources fail | Return error with diagnostic info |

## Cost Optimisation

```yaml
# Caching reduces repeat queries
cache_hit_rate: 45%
estimated_monthly_savings: $120

# Fallbacks use cheaper alternatives
primary_api_calls: 60%
fallback_api_calls: 40%
cost_per_query:
  with_fallbacks: $0.02
  without_fallbacks: $0.05
```

## See Also

- [fan-out](../../_combinators/fan-out/) - Parallel execution
- [try-first](../../_combinators/try-first/) - Fallback chains
- [with-retry](../../_decorators/with-retry/) - Retry logic
- [with-cache](../../_decorators/with-cache/) - Caching
- [intent-refiner](../../_meta/intent-refiner/) - Learn preferences
