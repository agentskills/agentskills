---
name: filter-skill
description: Filter a list by applying a predicate skill to each item, keeping only items where the predicate returns true.
level: 2
operation: READ
type_params:
  - name: A
    description: Item type
inputs:
  - name: items
    type: A[]
    required: true
    description: List of items to filter
  - name: predicate
    type: Skill<A, boolean>
    required: true
    description: Skill that returns true for items to keep
  - name: parallel
    type: boolean
    required: false
    default: true
    description: Whether to evaluate predicates in parallel
outputs:
  - name: results
    type: A[]
    description: Items where predicate returned true
  - name: rejected
    type: A[]
    description: Items where predicate returned false
  - name: rejection_rate
    type: number
    description: Fraction of items rejected (0.0 to 1.0)
---

# filter-skill

Filter a collection using a skill as the predicate function.

## Functional Signature

```
filter-skill :: ∀A. (A[], Skill<A, boolean>) → A[]
```

Equivalent to Haskell's `filter`:

```haskell
filter :: (a -> Bool) -> [a] -> [a]
```

## Why This Matters

Filtering is fundamental to agent workflows:
- **Triage**: Which emails need action?
- **Qualification**: Which leads are worth pursuing?
- **Validation**: Which API responses are usable?
- **Moderation**: Which content is appropriate?

Making the predicate a skill means:
- Complex logic can be encapsulated
- LLM-based classification becomes composable
- Predicates can be tested independently

## Usage Examples

### Triage urgent emails

```yaml
steps:
  - skill: filter-skill
    inputs:
      items: ${emails}
      predicate: is-urgent
    outputs:
      results: urgent_emails
      rejected: can_wait
```

### Qualify leads with AI

```yaml
steps:
  - skill: filter-skill
    inputs:
      items: ${leads}
      predicate: is-qualified-lead  # LLM-based qualification
    outputs:
      results: qualified
      rejection_rate: qualification_rate
```

### Chain filters (AND logic)

```yaml
# Keep items that pass ALL predicates
steps:
  - skill: filter-skill
    inputs:
      items: ${candidates}
      predicate: has-required-skills
    outputs:
      results: with_skills

  - skill: filter-skill
    inputs:
      items: ${with_skills}
      predicate: in-salary-range
    outputs:
      results: matched

  - skill: filter-skill
    inputs:
      items: ${matched}
      predicate: available-to-start
    outputs:
      results: final_candidates
```

### Partition with rejected items

```yaml
steps:
  - skill: filter-skill
    inputs:
      items: ${support_tickets}
      predicate: requires-human-escalation
    outputs:
      results: escalate_to_human
      rejected: auto_respond

  # Handle each partition differently
  - skill: map-skill
    inputs:
      items: ${auto_respond}
      processor: generate-auto-response

  - skill: map-skill
    inputs:
      items: ${escalate_to_human}
      processor: prepare-escalation-brief
```

## Type Safety

The type checker validates:

1. **Predicate signature**: Must be `Skill<A, boolean>`
2. **Type preservation**: Output items have same type as input
3. **Boolean return**: Predicate must return exactly `boolean`

```yaml
# This will fail type checking:
- skill: filter-skill
  inputs:
    items: ${emails}
    predicate: summarize-email  # Returns string, not boolean
  # ERROR: Predicate must return boolean, got string
```

## Creating Predicate Skills

A predicate skill returns boolean:

```yaml
---
name: is-urgent
level: 1
operation: READ
inputs:
  - name: item
    type: Email
outputs:
  - name: result
    type: boolean
    description: True if email requires immediate attention
---

# is-urgent

Evaluate whether an email requires immediate attention.

## Criteria

Return `true` if ANY of:
- Subject contains "urgent", "asap", "critical"
- Sender is in VIP list
- Thread has been waiting > 24 hours
- Contains deadline within 48 hours
```

## Combining Predicates

### OR logic (any predicate)

```yaml
# Custom skill that ORs multiple predicates
name: any-of
inputs:
  - name: item
    type: A
  - name: predicates
    type: Skill<A, boolean>[]
outputs:
  - name: result
    type: boolean
```

### NOT logic (invert)

```yaml
# Keep items that DON'T match
- skill: filter-skill
  inputs:
    items: ${emails}
    predicate: is-spam
  outputs:
    rejected: not_spam  # Use rejected output
```

## Performance Characteristics

| Scenario | Behaviour |
|----------|-----------|
| `parallel: true` | Predicates evaluated concurrently |
| `parallel: false` | Sequential evaluation, short-circuit possible |
| Empty input | Returns `[]` immediately |
| All pass | Returns original list |
| None pass | Returns `[]` |

## See Also

- [map-skill](../map-skill/) - Transform items
- [reduce-skill](../reduce-skill/) - Aggregate items
- [try-first](../try-first/) - First successful result
