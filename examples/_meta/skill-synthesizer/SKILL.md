---
name: skill-synthesizer
description: Generate new skill definitions from task descriptions, examples, or observed execution patterns. Enables automatic skill creation and workflow optimisation.
level: 3
operation: WRITE
inputs:
  - name: task_description
    type: string
    required: true
    description: Natural language description of what the skill should do
  - name: example_inputs
    type: any[]
    required: false
    description: Example inputs the skill should handle
  - name: example_outputs
    type: any[]
    required: false
    description: Expected outputs for the example inputs
  - name: available_skills
    type: Skill[]
    required: true
    description: Skills available for composition
  - name: constraints
    type: SkillConstraints
    required: false
    description: Requirements (max latency, cost, required accuracy)
  - name: execution_trace
    type: ExecutionGraph
    required: false
    description: Observed execution to codify into a skill
  - name: style
    type: enum[minimal, balanced, comprehensive]
    required: false
    default: balanced
    description: How detailed the generated skill should be
outputs:
  - name: generated_skill
    type: SkillDefinition
    description: The synthesised skill definition
  - name: composition_graph
    type: ExecutionGraph
    description: How available skills are composed
  - name: type_signature
    type: TypeSignature
    description: Inferred input/output types
  - name: test_results
    type: TestResult[]
    min_items: 1
    description: Validation against examples
  - name: confidence
    type: number
    range: [0, 1]
    description: Confidence the skill meets requirements
  - name: alternatives
    type: SkillDefinition[]
    description: Alternative implementations considered
---

# skill-synthesizer

Automatically generate skill definitions from descriptions, examples, or traces.

## Why This Matters

Creating skills manually is time-consuming:
- **Repetitive patterns**: Similar compositions appear often
- **Expertise required**: Need to know available skills
- **Testing burden**: Must verify correctness
- **Maintenance**: Keep up with skill library changes

`skill-synthesizer` provides:
- **Natural language → Skill**: Describe what you want
- **Example-driven**: Show inputs and outputs
- **Trace codification**: Turn ad-hoc executions into reusable skills
- **Automatic composition**: Find optimal skill combinations

## The Synthesis Process

```
Task Description + Examples + Available Skills
                    ↓
            Type Inference
                    ↓
            Skill Search (find candidates)
                    ↓
            Composition Planning
                    ↓
            Validation (test against examples)
                    ↓
            Optimisation (meet constraints)
                    ↓
            Generated Skill Definition
```

## Usage Examples

### From natural language

```yaml
steps:
  - skill: skill-synthesizer
    inputs:
      task_description: |
        Research a company and generate a one-page briefing.
        Include recent news, financial summary, and key people.
      available_skills: ${skill_library}
    outputs:
      generated_skill: company_briefing_skill
      composition_graph: how_it_works
```

Generated skill:
```yaml
---
name: company-briefing
description: Generate a one-page company briefing with news, financials, and key people.
level: 3
operation: READ
composes:
  - fan-out
  - company-news-search
  - financial-data-fetch
  - key-people-lookup
  - briefing-template-fill
inputs:
  - name: company
    type: string
outputs:
  - name: briefing
    type: Document
---
```

### From examples (input/output pairs)

```yaml
steps:
  - skill: skill-synthesizer
    inputs:
      task_description: "Convert meeting notes to action items"
      example_inputs:
        - "Meeting with Alice: Discussed Q4 goals. Alice to send proposal by Friday."
        - "Call with Bob: Review contract terms. Need legal review before signing."
      example_outputs:
        - [{ assignee: "Alice", action: "Send proposal", due: "Friday" }]
        - [{ assignee: "Legal", action: "Review contract", due: null }]
      available_skills: ${skill_library}
    outputs:
      generated_skill: meeting_to_actions
      test_results: validation
```

### From execution trace

```yaml
steps:
  # First, explain what happened
  - skill: explain-execution
    inputs:
      observed_input: ${input}
      observed_output: ${output}
      skill_library: ${skills}
    outputs:
      likely_paths: execution_trace

  # Then, codify into reusable skill
  - skill: skill-synthesizer
    inputs:
      task_description: "Replicate this successful execution"
      execution_trace: ${execution_trace[0]}
      available_skills: ${skills}
    outputs:
      generated_skill: codified_workflow
```

### With constraints

```yaml
steps:
  - skill: skill-synthesizer
    inputs:
      task_description: "Fast company lookup for real-time use"
      available_skills: ${skill_library}
      constraints:
        max_latency: 2s
        max_cost: 0.01
        required_fields: ["name", "industry", "size"]
    outputs:
      generated_skill: fast_company_lookup
      # Will prefer cached skills, simpler compositions
```

## Type Inference

The synthesizer infers types from:

### Example analysis

```yaml
example_inputs:
  - "AAPL"
  - "GOOGL"
# Inferred: input is stock_symbol: string

example_outputs:
  - { price: 150.25, change: 2.3 }
  - { price: 140.50, change: -1.2 }
# Inferred: output is { price: number, change: number }
```

### Description parsing

```yaml
task_description: "Given a company name, return their stock price"
# Inferred:
#   input: { company_name: string }
#   output: { stock_price: number }
```

### Available skill matching

```yaml
# If stock-price-lookup exists with signature:
# stock-price-lookup: Symbol → PriceData

# Synthesizer infers compatible composition
```

## Composition Strategies

### Direct match

Find single skill that does the job:

```yaml
task_description: "Search the web"
# → web-search (direct match)
```

### Sequential composition

Chain skills:

```yaml
task_description: "Search web and summarise results"
# → web-search | summarize
```

### Parallel composition

Fan out and merge:

```yaml
task_description: "Get data from multiple sources"
# → fan-out([source-a, source-b, source-c]) | merge
```

### Conditional composition

Branch based on input:

```yaml
task_description: "Handle different document types"
# → classify-document | branch(pdf: pdf-parse, doc: doc-parse, ...)
```

### Iterative composition

Apply until condition:

```yaml
task_description: "Research until we have 5 sources"
# → fix-point(λs. if len(s.sources) >= 5 then s else research-more(s))
```

## Validation

Generated skills are tested against examples:

```yaml
test_results:
  - input: "AAPL"
    expected: { price: 150.25, change: 2.3 }
    actual: { price: 150.25, change: 2.3 }
    status: pass

  - input: "INVALID"
    expected: { error: "Unknown symbol" }
    actual: { error: "Symbol not found" }
    status: pass  # Semantic match
```

## Optimisation

When constraints are specified:

```yaml
constraints:
  max_latency: 5s
  prefer: ["accuracy", "cost"]

# Synthesizer will:
# 1. Estimate latency of each composition
# 2. Prune compositions exceeding 5s
# 3. Rank remaining by accuracy, then cost
# 4. Return optimal + alternatives
```

## Generated Skill Quality

| Style | Characteristics |
|-------|-----------------|
| `minimal` | Bare essentials, no error handling |
| `balanced` | Standard error handling, basic docs |
| `comprehensive` | Full error handling, extensive docs, examples |

```yaml
style: comprehensive
# Generates:
# - Detailed description
# - Input validation
# - Error handling for each composed skill
# - Usage examples
# - Edge case documentation
```

## Alternatives

Synthesizer returns alternatives when:

```yaml
outputs:
  generated_skill: optimal_solution
  confidence: 0.85

  alternatives:
    - skill: faster_but_less_accurate
      trade_off: "2x faster, 10% less accurate"
      confidence: 0.75

    - skill: more_accurate_but_slower
      trade_off: "15% more accurate, 3x slower"
      confidence: 0.80
```

## Human-in-the-Loop

For low confidence synthesis:

```yaml
outputs:
  confidence: 0.45  # Below threshold

  clarification_needed:
    - "Should 'company research' include financial data?"
    - "What format should the output be?"

  partial_skill: incomplete_definition
```

## Integration with Intent Refiner

Continuous improvement loop:

```yaml
steps:
  # Generate initial skill
  - skill: skill-synthesizer
    inputs:
      task_description: ${user_request}
    outputs:
      generated_skill: v1

  # Execute and get feedback
  - skill: ${v1}
    outputs:
      result: output

  - skill: intent-refiner
    inputs:
      original_request: ${user_request}
      execution_result: ${output}
      user_action: ${feedback}
    outputs:
      refined_intent: better_understanding

  # Regenerate with refined understanding
  - skill: skill-synthesizer
    inputs:
      task_description: ${better_understanding}
      constraints: ${learned_preferences}
    outputs:
      generated_skill: v2  # Improved version
```

## Limitations

| Challenge | Mitigation |
|-----------|------------|
| Ambiguous descriptions | Ask clarifying questions |
| No matching skills | Suggest skill gaps to fill |
| Conflicting examples | Highlight conflicts, ask user |
| Complex compositions | Limit depth, prefer simple |

## See Also

- [explain-execution](../explain-execution/) - Understand executions
- [intent-refiner](../intent-refiner/) - Learn preferences
- [reduce-skill](../../_combinators/reduce-skill/) - Combine results
