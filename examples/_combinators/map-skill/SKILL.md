---
name: map-skill
description: Apply a skill to each item in a list, returning transformed results. The functional programming 'map' operation for skills.
level: 2
operation: READ
type_params:
  - name: A
    description: Input item type
  - name: B
    description: Output item type
inputs:
  - name: items
    type: A[]
    required: true
    description: List of items to process
  - name: processor
    type: Skill<A, B>
    required: true
    description: Skill to apply to each item
  - name: parallel
    type: boolean
    required: false
    default: true
    description: Whether to process items in parallel
  - name: max_concurrency
    type: integer
    required: false
    default: 10
    description: Maximum parallel executions (when parallel=true)
outputs:
  - name: results
    type: B[]
    description: Transformed items in same order as input
  - name: execution_time
    type: duration
    description: Total execution time
  - name: parallelism_achieved
    type: number
    description: Effective parallelism ratio (1.0 = fully parallel)
---

# map-skill

The fundamental higher-order combinator for applying a skill to each item in a collection.

## Functional Signature

```
map-skill :: ∀A B. (A[], Skill<A, B>, Options) → B[]
```

This is the skills equivalent of Haskell's `map`:

```haskell
map :: (a -> b) -> [a] -> [b]
```

## Why This Matters

Without `map-skill`, processing a list requires:
1. Manual iteration in workflow instructions
2. Error handling repeated for each item
3. No parallelism guarantees
4. Type safety lost at each step

With `map-skill`:
1. Single declarative call
2. Consistent error handling
3. Automatic parallelism
4. End-to-end type checking

## Usage Examples

### Basic: Summarise emails

```yaml
steps:
  - skill: map-skill
    inputs:
      items: ${emails}
      processor: summarize-email
    outputs:
      results: summaries
```

### With concurrency control

```yaml
steps:
  - skill: map-skill
    inputs:
      items: ${companies}
      processor: company-research
      parallel: true
      max_concurrency: 5  # Respect API rate limits
    outputs:
      results: company_profiles
```

### Chained transformations

```yaml
# Equivalent to: map score . map enrich . map validate
steps:
  - skill: map-skill
    inputs:
      items: ${leads}
      processor: validate-lead
    outputs:
      results: validated

  - skill: map-skill
    inputs:
      items: ${validated}
      processor: enrich-lead
    outputs:
      results: enriched

  - skill: map-skill
    inputs:
      items: ${enriched}
      processor: score-lead
    outputs:
      results: scored_leads
```

## Type Safety

The type checker validates:

1. **Input compatibility**: Items must match processor's input type
2. **Output propagation**: Result type is `processor.output_type[]`
3. **Skill constraints**: Processor must be a valid `Skill<A, B>`

```yaml
# This will fail type checking:
- skill: map-skill
  inputs:
    items: ${flights}        # Flight[]
    processor: summarize-email  # Skill<Email, string>
  # ERROR: Flight is not compatible with Email
```

## Error Handling

By default, `map-skill` uses fail-fast semantics. For resilient processing, compose with decorators:

```yaml
- skill: map-skill
  inputs:
    items: ${urls}
    processor:
      skill: with-retry
      inputs:
        target: fetch-url
        max_attempts: 3
```

Or use `filter-skill` to handle partial failures:

```yaml
- skill: map-skill
  inputs:
    items: ${urls}
    processor: try-fetch-url  # Returns Result<Page, Error>
  outputs:
    results: fetch_results

- skill: filter-skill
  inputs:
    items: ${fetch_results}
    predicate: is-success
  outputs:
    results: successful_pages
```

## Performance Characteristics

| Scenario | Behaviour |
|----------|-----------|
| `parallel: true` | Items processed concurrently up to `max_concurrency` |
| `parallel: false` | Sequential processing, order guaranteed |
| Empty input | Returns `[]` immediately |
| Single item | Equivalent to direct skill invocation |

## Comparison with Imperative Approach

**Without map-skill** (imperative):
```
For each email in inbox:
  1. Call summarize-email
  2. Handle errors
  3. Append to results
Return results
```

**With map-skill** (declarative):
```yaml
map-skill(inbox, summarize-email)
```

The declarative version is:
- Shorter
- Type-checked
- Automatically parallelised
- Consistent error handling

## See Also

- [filter-skill](../filter-skill/) - Filter items by predicate
- [reduce-skill](../reduce-skill/) - Fold list to single value
- [fan-out](../fan-out/) - Apply multiple skills to same input
