---
name: reduce-skill
description: Reduce a list to a single value by iteratively applying a combining skill. The functional programming 'fold' operation.
level: 2
operation: READ
type_params:
  - name: A
    description: Input item type
  - name: B
    description: Accumulator/result type
inputs:
  - name: items
    type: A[]
    required: true
    description: List of items to reduce
  - name: reducer
    type: Skill<{accumulator: B, item: A}, B>
    required: true
    description: Skill that combines accumulator with next item
  - name: initial
    type: B
    required: true
    description: Initial accumulator value
  - name: direction
    type: enum[left, right]
    required: false
    default: left
    description: Fold direction (left = head first, right = tail first)
outputs:
  - name: result
    type: B
    description: Final accumulated value
  - name: intermediate_states
    type: B[]
    description: Accumulator value after each step (for debugging)
---

# reduce-skill

Collapse a collection into a single value using a combining skill.

## Functional Signature

```
reduce-skill :: ∀A B. (A[], Skill<(B, A), B>, B) → B
```

Equivalent to Haskell's `foldl`:

```haskell
foldl :: (b -> a -> b) -> b -> [a] -> b
```

## Why This Matters

Many agent tasks are reductions:
- **Summarisation**: Many documents → one summary
- **Aggregation**: Many data points → one report
- **Consensus**: Many opinions → one decision
- **Scoring**: Many signals → one score

Making the reducer a skill means:
- LLM can perform semantic aggregation
- Complex combining logic is encapsulated
- Intermediate states are observable

## Usage Examples

### Synthesise research findings

```yaml
steps:
  - skill: reduce-skill
    inputs:
      items: ${research_sources}
      reducer: synthesize-finding
      initial: { summary: "", sources: [] }
    outputs:
      result: final_synthesis
```

### Calculate aggregate score

```yaml
steps:
  - skill: reduce-skill
    inputs:
      items: ${evaluation_criteria}
      reducer: weighted-score-accumulator
      initial: { score: 0, weight_sum: 0 }
    outputs:
      result: final_evaluation
```

### Build consensus from reviews

```yaml
steps:
  - skill: reduce-skill
    inputs:
      items: ${reviewer_opinions}
      reducer: merge-opinions
      initial: {
        consensus: null,
        agreements: [],
        disagreements: []
      }
    outputs:
      result: consensus_report
```

### Chain of thought accumulation

```yaml
steps:
  - skill: reduce-skill
    inputs:
      items: ${reasoning_steps}
      reducer: accumulate-reasoning
      initial: {
        conclusion: null,
        confidence: 0,
        chain: []
      }
    outputs:
      result: reasoned_conclusion
      intermediate_states: thought_chain
```

## Type Safety

The type checker validates:

1. **Reducer signature**: Must accept `{accumulator: B, item: A}` and return `B`
2. **Initial type**: Must match accumulator type `B`
3. **Output type**: Result is `B`

```yaml
# This will fail type checking:
- skill: reduce-skill
  inputs:
    items: ${numbers}           # number[]
    reducer: add-numbers        # Skill<(number, number), number>
    initial: "start"            # string, but should be number
  # ERROR: initial type 'string' doesn't match accumulator type 'number'
```

## Creating Reducer Skills

A reducer combines accumulator with item:

```yaml
---
name: synthesize-finding
level: 1
operation: READ
inputs:
  - name: accumulator
    type: SynthesisState
  - name: item
    type: ResearchSource
outputs:
  - name: result
    type: SynthesisState
---

# synthesize-finding

Integrate a new research source into the running synthesis.

## Process

1. Extract key claims from the new source
2. Check for contradictions with existing synthesis
3. Merge compatible findings
4. Note disagreements with citations
5. Update confidence based on source quality
```

## Parallel Reductions

For associative operations, parallel reduction is possible:

```yaml
steps:
  # Split into chunks, reduce each in parallel
  - skill: map-skill
    inputs:
      items: ${chunks_of_items}
      processor:
        skill: reduce-skill
        inputs:
          reducer: combine-scores
          initial: 0
    outputs:
      results: partial_sums

  # Final reduction of partial results
  - skill: reduce-skill
    inputs:
      items: ${partial_sums}
      reducer: combine-scores
      initial: 0
    outputs:
      result: total
```

## Common Reduction Patterns

| Pattern | Initial | Reducer Logic |
|---------|---------|---------------|
| Sum | `0` | `acc + item` |
| Product | `1` | `acc * item` |
| Max | `-∞` | `max(acc, item)` |
| Concatenate | `[]` | `acc ++ [item]` |
| Merge objects | `{}` | `{...acc, ...item}` |
| Build summary | `""` | `acc + summarize(item)` |

## See Also

- [map-skill](../map-skill/) - Transform items
- [filter-skill](../filter-skill/) - Select items
- [fan-out](../fan-out/) - Multiple skills, one input
