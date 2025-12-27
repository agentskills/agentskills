---
name: intent-refiner
description: Learn user preferences and refine intent understanding from feedback on skill executions. Enables adaptive workflows that improve over time.
level: 3
operation: READ
inputs:
  - name: original_request
    type: string
    required: true
    description: The user's original natural language request
  - name: generated_plan
    type: ExecutionGraph
    required: true
    description: The plan/workflow that was generated
  - name: execution_result
    type: any
    required: true
    description: What the execution produced
  - name: user_action
    type: enum[accepted, rejected, modified]
    required: true
    description: How the user responded to the result
  - name: user_modification
    type: any
    required: false
    description: If modified, what changes the user made
  - name: user_feedback
    type: string
    required: false
    description: Explicit feedback from the user
  - name: historical_feedback
    type: FeedbackRecord[]
    required: false
    description: Previous feedback from this user
outputs:
  - name: refined_intent
    type: Intent
    requires_rationale: true
    description: Updated understanding of what user actually wanted
  - name: learned_preferences
    type: PreferenceUpdate[]
    description: New preferences learned from this interaction
  - name: suggested_defaults
    type: SkillConfig
    description: Recommended default configurations for future runs
  - name: confidence_delta
    type: number
    description: How much this feedback changed our understanding
  - name: explanation
    type: string
    requires_rationale: true
    description: What we learned and why
---

# intent-refiner

Learn from user feedback to improve future skill executions.

## Why This Matters

Users rarely express exactly what they want:
- **Implicit preferences**: "Find flights" (but actually wants direct flights)
- **Context-dependent**: Same request, different situations
- **Evolving needs**: Preferences change over time
- **Unspoken constraints**: Budget, time, quality trade-offs

`intent-refiner` provides:
- **Preference learning**: Infer constraints from accept/reject
- **Intent clarification**: Understand what they really meant
- **Adaptive defaults**: Configure skills based on history
- **Feedback loop**: Continuous improvement

## The Learning Loop

```
User Request → Generate Plan → Execute → Present Result
                                              ↓
                              User: Accept / Reject / Modify
                                              ↓
                                    intent-refiner
                                              ↓
                              Learned Preferences
                                              ↓
                              Better Future Plans
```

## Usage Examples

### Learn from rejection

```yaml
steps:
  - skill: intent-refiner
    inputs:
      original_request: "Find flights to Tokyo"
      generated_plan: ${flight_search_plan}
      execution_result:
        flights:
          - { airline: "United", stops: 2, price: 600 }
          - { airline: "ANA", stops: 0, price: 1200 }
      user_action: rejected
      user_feedback: "Too many stops"
    outputs:
      learned_preferences:
        - preference: "max_stops"
          value: 0
          confidence: 0.8
      suggested_defaults:
        flight-search:
          max_stops: 0
```

### Learn from modification

```yaml
steps:
  - skill: intent-refiner
    inputs:
      original_request: "Summarize this document"
      execution_result: { summary: "..." , length: 500 }
      user_action: modified
      user_modification: { summary: "...", length: 150 }  # User shortened it
    outputs:
      learned_preferences:
        - preference: "summary_length"
          value: "concise"
          confidence: 0.7
      explanation: |
        "User shortened summary from 500 to 150 words.
        Likely prefers concise summaries. Will default to
        shorter outputs in future."
```

### Learn from acceptance

```yaml
steps:
  - skill: intent-refiner
    inputs:
      original_request: "Research this company"
      execution_result: ${detailed_research}
      user_action: accepted
      historical_feedback:
        - { request: "Research X", accepted: true, depth: "detailed" }
        - { request: "Research Y", accepted: true, depth: "detailed" }
    outputs:
      learned_preferences:
        - preference: "research_depth"
          value: "detailed"
          confidence: 0.9  # Reinforced by history
```

## Preference Types

### Explicit preferences

Stated directly by user:

```yaml
learned_preferences:
  - preference: "max_price"
    value: 500
    source: "user_feedback"
    confidence: 1.0
```

### Implicit preferences

Inferred from behaviour:

```yaml
learned_preferences:
  - preference: "prefers_direct_flights"
    value: true
    source: "rejection_pattern"
    confidence: 0.75
    evidence: "Rejected 3 itineraries with stops, accepted direct"
```

### Contextual preferences

Depend on situation:

```yaml
learned_preferences:
  - preference: "summary_length"
    value: "brief"
    context: { document_type: "email" }
    confidence: 0.8
  - preference: "summary_length"
    value: "detailed"
    context: { document_type: "research_paper" }
    confidence: 0.7
```

## Suggested Defaults

Transform preferences into skill configurations:

```yaml
# Input: learned_preferences
- { preference: "max_stops", value: 0 }
- { preference: "preferred_airlines", value: ["ANA", "JAL"] }
- { preference: "price_sensitivity", value: "high" }

# Output: suggested_defaults
flight-search:
  max_stops: 0
  airlines: ["ANA", "JAL"]
  sort_by: "price"

hotel-search:
  sort_by: "price"  # Inferred from price_sensitivity
```

## Confidence and Decay

Preferences have confidence that:
- **Increases** with consistent feedback
- **Decreases** over time without reinforcement
- **Resets** on contradictory feedback

```yaml
learned_preferences:
  - preference: "max_stops"
    value: 0
    confidence: 0.9
    last_reinforced: "2024-03-15"
    decay_rate: 0.1  # per month

  - preference: "airline_preference"
    value: "ANA"
    confidence: 0.5  # Older, less certain
    last_reinforced: "2024-01-10"
```

## Historical Analysis

With accumulated feedback, identify patterns:

```yaml
inputs:
  historical_feedback:
    - { request: "...", context: { time: "morning" }, accepted: true }
    - { request: "...", context: { time: "evening" }, rejected: true }
    - { request: "...", context: { time: "morning" }, accepted: true }

outputs:
  learned_preferences:
    - preference: "preferred_execution_time"
      value: "morning"
      confidence: 0.7
      explanation: "User tends to accept morning results, reject evening ones"
```

## Integration with Workflows

### Before execution

```yaml
steps:
  # Load user preferences
  - skill: load-preferences
    inputs:
      user_id: ${user}
    outputs:
      preferences: user_prefs

  # Configure skills with preferences
  - skill: flight-search
    inputs:
      query: ${query}
      config: ${user_prefs.flight-search}  # Apply learned defaults
```

### After execution

```yaml
steps:
  # Present result and collect feedback
  - skill: present-to-user
    inputs:
      result: ${execution_result}
    outputs:
      action: user_action
      modification: user_modification

  # Learn from feedback
  - skill: intent-refiner
    inputs:
      original_request: ${request}
      execution_result: ${execution_result}
      user_action: ${user_action}
      user_modification: ${user_modification}
    outputs:
      learned_preferences: new_prefs

  # Store for future
  - skill: store-preferences
    inputs:
      user_id: ${user}
      updates: ${new_prefs}
```

## Privacy Considerations

| Data | Handling |
|------|----------|
| Preferences | Stored per-user, not shared |
| Request history | Summarised, not raw |
| Feedback | Anonymised for aggregate analysis |
| Modifications | Content not stored, only patterns |

## Bootstrapping

For new users without history:

```yaml
inputs:
  historical_feedback: []
  similar_users: ${cohort_preferences}  # Optional

outputs:
  suggested_defaults: ${cohort_defaults}  # Use cohort baseline
  explanation: "No personal history. Using defaults from similar users."
```

## Limitations

| Challenge | Mitigation |
|-----------|------------|
| Preference conflicts | Recency weighting, explicit override |
| Context ambiguity | Ask for clarification threshold |
| Over-fitting | Minimum sample size before applying |
| Preference drift | Time decay, periodic confirmation |

## See Also

- [explain-execution](../explain-execution/) - Understand what happened
- [skill-synthesizer](../skill-synthesizer/) - Generate optimised workflows
- [with-logging](../../_decorators/with-logging/) - Capture feedback data
