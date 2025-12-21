---
name: explain-execution
description: Reconstruct and explain what happened inside a skill execution from observed inputs, outputs, and execution traces. Essential for debugging, auditing, and understanding agent behaviour.
level: 3
operation: READ
inputs:
  - name: observed_input
    type: any
    required: true
    description: The input that was provided to the skill/workflow
  - name: observed_output
    type: any
    required: true
    description: The output that was produced
  - name: skill_library
    type: SkillSignature[]
    required: true
    description: Available skills with their type signatures
  - name: execution_logs
    type: LogEntry[]
    required: false
    description: Execution logs if available (improves accuracy)
  - name: execution_duration
    type: duration
    required: false
    description: Total execution time (helps narrow possibilities)
  - name: max_depth
    type: integer
    required: false
    default: 5
    description: Maximum composition depth to consider
outputs:
  - name: likely_paths
    type: ExecutionGraph[]
    description: Ranked list of possible execution paths
    min_items: 1
  - name: confidence
    type: number
    range: [0, 1]
    description: Confidence in the top explanation
  - name: explanation
    type: string
    requires_rationale: true
    description: Human-readable explanation of what likely happened
  - name: evidence
    type: Evidence[]
    requires_source: true
    description: Evidence supporting the explanation
  - name: alternative_explanations
    type: string[]
    description: Other plausible interpretations
---

# explain-execution

Reverse-engineer what happened inside a skill execution from observable data.

## Why This Matters

Agent systems often operate as "black boxes":
- **Complex compositions**: Many skills chained together
- **Dynamic selection**: Runtime skill choices
- **Nested workflows**: Skills calling skills
- **Parallel execution**: Multiple paths simultaneously

`explain-execution` provides:
- **Post-hoc understanding**: What did the agent do?
- **Debugging**: Why did it fail?
- **Auditing**: Was the process correct?
- **Learning**: How did it succeed?

## The Insight: Type-Directed Reconstruction

Given:
- Input type: `Query`
- Output type: `Report`
- Available skills with signatures

We can infer:
- Which skills could have produced this output from this input
- What intermediate types were likely involved
- What composition structure was used

This is **type inference for execution traces**.

## Usage Examples

### Debug a failed workflow

```yaml
steps:
  - skill: explain-execution
    inputs:
      observed_input: ${original_request}
      observed_output: ${error_response}
      skill_library: ${available_skills}
      execution_logs: ${logs_if_available}
    outputs:
      explanation: what_went_wrong
      evidence: supporting_data
```

### Audit a successful completion

```yaml
steps:
  - skill: explain-execution
    inputs:
      observed_input: { query: "Find best flights to Tokyo" }
      observed_output: { recommendation: "JAL 123", price: 850 }
      skill_library: ${flight_booking_skills}
    outputs:
      likely_paths: execution_paths
      explanation: process_summary
```

### Understand model behaviour

```yaml
# What did the agent actually do?
steps:
  - skill: explain-execution
    inputs:
      observed_input: ${user_prompt}
      observed_output: ${agent_response}
      skill_library: ${all_available_skills}
      execution_duration: 45s
    outputs:
      likely_paths: inferred_workflow
      confidence: certainty
```

## Type-Directed Inference

### Step 1: Identify terminal skills

Find skills that produce the output type:

```
Output: Report
Skills producing Report:
  - generate-report: (Data, Template) → Report
  - summarize-to-report: Document[] → Report
```

### Step 2: Work backwards

For each candidate, find what produces its inputs:

```
generate-report needs (Data, Template)
  - fetch-data: Query → Data ✓ (matches input type)
  - load-template: string → Template

summarize-to-report needs Document[]
  - search-documents: Query → Document[] ✓ (matches input type)
```

### Step 3: Score paths

Rank by:
- Type compatibility
- Execution duration plausibility
- Log evidence (if available)
- Skill usage patterns

### Step 4: Explain

Generate human-readable explanation:

```
"The input Query was most likely processed by:
1. search-documents: Found relevant documents
2. summarize-to-report: Generated the final report

Confidence: 85%

Evidence:
- Output contains document references matching search results
- Execution time (45s) consistent with document search + summarisation"
```

## Evidence Types

```typescript
interface Evidence {
  type: "type_match" | "timing" | "log_entry" | "output_content" | "pattern";
  description: string;
  weight: number;  // Contribution to confidence
  source: string;  // Where this evidence came from
}
```

Examples:
- **type_match**: Input/output types align with skill signature
- **timing**: Execution duration matches expected skill performance
- **log_entry**: Explicit log of skill invocation
- **output_content**: Output structure matches skill's typical output
- **pattern**: Matches known composition patterns

## Handling Uncertainty

When multiple paths are plausible:

```yaml
outputs:
  likely_paths:
    - path: [fetch-data, generate-report]
      probability: 0.65
    - path: [search-documents, summarize-to-report]
      probability: 0.30
    - path: [cached-lookup]
      probability: 0.05

  alternative_explanations:
    - "Could have used cached results if data was recently fetched"
    - "Parallel execution of search + fetch also possible"
```

## With Execution Logs

When logs are available, accuracy improves dramatically:

```yaml
inputs:
  execution_logs:
    - { skill: "web-search", status: "success", duration: 2.3s }
    - { skill: "summarize", status: "success", duration: 5.1s }

outputs:
  confidence: 0.98  # Much higher with logs
  likely_paths:
    - path: [web-search, summarize]
      probability: 0.98
```

## Applications

### 1. Debugging

```yaml
# Why did this fail?
- skill: explain-execution
  inputs:
    observed_output: { error: "Rate limit exceeded" }
    # ...
  outputs:
    explanation: |
      "The workflow likely used external-api-call repeatedly
      without rate limiting. The fan-out over 50 items
      triggered the API's rate limit."
```

### 2. Auditing

```yaml
# Was sensitive data handled correctly?
- skill: explain-execution
  inputs:
    skill_library: ${skills_with_data_classification}
    # ...
  outputs:
    evidence:
      - type: "pattern"
        description: "PII passed through redact-skill before storage"
```

### 3. Learning from success

```yaml
# How did the agent solve this efficiently?
- skill: explain-execution
  inputs:
    execution_duration: 3s  # Unusually fast
    # ...
  outputs:
    explanation: |
      "Cache hit on company-research avoided 15s API call.
      Consider expanding cache TTL for similar queries."
```

### 4. Reproducing behaviour

```yaml
# Turn inferred path into explicit workflow
- skill: explain-execution
  outputs:
    likely_paths: inferred

- skill: skill-synthesizer
  inputs:
    execution_graph: ${inferred[0]}
  outputs:
    generated_skill: reproducible_workflow
```

## Limitations

| Scenario | Challenge |
|----------|-----------|
| Non-deterministic skills | Multiple runs → different paths |
| Dynamic skill selection | Runtime choices not in signature |
| External side effects | Effects not visible in output |
| Parallel execution | Order ambiguity |
| Nested compositions | Exponential path possibilities |

## See Also

- [intent-refiner](../intent-refiner/) - Learn from user feedback
- [skill-synthesizer](../skill-synthesizer/) - Generate skills from traces
- [with-logging](../../_decorators/with-logging/) - Generate logs for analysis
