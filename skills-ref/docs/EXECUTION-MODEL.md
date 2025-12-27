# Execution Model

This document defines the precise execution semantics for AgentSkills skill composition.

## Overview

The execution model defines how skills execute, how state flows between them, and how errors are handled. Understanding these semantics is critical for building reliable workflows.

## Sequential Execution (Default)

Skills execute in declaration order. Each skill receives outputs from all previous skills.

```yaml
skill: data-pipeline
composes:
  - fetch-data       # Runs first
  - transform-data   # Runs second, receives fetch-data output
  - save-data        # Runs third, receives all previous outputs
```

### Execution Order Guarantees

1. Skills execute **strictly in order**
2. A skill only starts after the previous skill completes
3. All outputs are available to subsequent skills
4. Order is deterministic and reproducible

## State Threading

Outputs accumulate in an **execution context** that flows through the chain.

```python
# Execution context structure
ExecutionContext:
  inputs: Dict[str, Any]       # Initial inputs
  outputs: Dict[str, Any]      # Accumulated outputs
  metadata: Dict[str, Any]     # Execution metadata
  trace_id: str                # Distributed tracing
```

### How State Flows

```
Initial inputs: {"query": "test"}

┌─────────────┐
│  fetch-data │ ← Receives: {query: "test"}
└──────┬──────┘
       │ Produces: {raw_data: [...]}
       ▼
┌─────────────┐
│  transform  │ ← Receives: {query: "test", raw_data: [...]}
└──────┬──────┘
       │ Produces: {processed: [...]}
       ▼
┌─────────────┐
│  save-data  │ ← Receives: {query: "test", raw_data: [...], processed: [...]}
└─────────────┘

Final context: {query, raw_data, processed, save_result}
```

### Field Mapping

Explicit mapping transforms output field names to input field names:

```yaml
transitions:
  - from: fetch-data
    to: transform
    mapping:
      raw_data: input_data    # fetch-data.raw_data → transform.input_data
      query: original_query   # Rename for clarity
```

### Implicit vs Explicit State

| Mode | Behaviour | Use Case |
|------|-----------|----------|
| Implicit | All outputs available to all subsequent skills | Simple chains |
| Explicit | Only mapped fields are passed | Complex chains, isolation |

**Default:** Implicit (all outputs available)

## Error Propagation

### Error Handling Strategies

```yaml
error_handling: STOP       # Stop on first error (default)
error_handling: CONTINUE   # Skip failed skill, continue chain
error_handling: COMPENSATE # Run compensation on failure
error_handling: RETRY      # Retry failed skill
```

### STOP Strategy (Default)

```
fetch-data ✓ → transform ✗ → save-data (never runs)
                    │
                    └→ Error propagates to caller
```

- First error stops execution
- Partial results are returned
- No cleanup performed (caller responsibility)

### CONTINUE Strategy

```
fetch-data ✓ → transform ✗ → save-data ✓
                    │
                    └→ Error logged, execution continues
```

- Failed skill's output is empty/null
- Subsequent skills must handle missing inputs
- All skills attempted regardless of failures
- Use for best-effort processing

### COMPENSATE Strategy

```
fetch-data ✓ → transform ✓ → save-data ✗
                                   │
                                   └→ Triggers compensation
                                            │
                                   ┌────────┴────────┐
                                   ▼                 ▼
                              rollback-save    notify-failure
```

- On failure, compensation skills run in reverse order
- Compensation skills receive the error and partial context
- Use for transactional workflows

### RETRY Strategy

```
fetch-data ✓ → transform ✗ (attempt 1)
                    │
                    └→ Wait (exponential backoff)
                            │
                            ▼
               transform ✗ (attempt 2)
                    │
                    └→ Wait (2x previous)
                            │
                            ▼
               transform ✓ (attempt 3)
                    │
                    ▼
               save-data
```

Configuration:
```yaml
max_retries: 3
retry_backoff_ms: 1000      # Initial delay
retry_backoff_multiplier: 2  # Exponential factor
retry_on: [TimeoutError, NetworkError]  # Which errors to retry
```

## Effect Classification

Skills are classified by their side effects:

| Effect | Description | Confirmation Required |
|--------|-------------|----------------------|
| `READ` | No side effects, idempotent | No |
| `WRITE` | Modifies external state | Yes |
| `TRANSFORM` | Transforms data, no external effects | No |

### Effect Composition (Monotonic)

**Rule:** The composed effect is the maximum of all component effects.

```
READ + READ = READ
READ + WRITE = WRITE
TRANSFORM + READ = TRANSFORM
TRANSFORM + WRITE = WRITE
WRITE + anything = WRITE
```

### Effect Validation

**Critical security guarantee:** A skill cannot claim a lower effect than its components.

```python
# This MUST fail validation:
skill: "safe-read"
operation: READ          # ← Claims READ
composes:
  - fetch-data           # READ ✓
  - delete-old-data      # WRITE ✗ Violation!
```

The validator performs **recursive effect checking**:

```python
def compute_transitive_effect(skill, available_skills):
    """Compute actual effect from composition tree."""
    max_effect = skill.declared_effect

    for composed_name in skill.composes:
        composed = available_skills[composed_name]
        composed_effect = compute_transitive_effect(composed, available_skills)
        max_effect = max(max_effect, composed_effect)

    return max_effect

def validate_effect(skill, available_skills):
    """Validate declared effect matches reality."""
    actual = compute_transitive_effect(skill, available_skills)
    if actual > skill.operation:
        raise SecurityError(
            f"Skill '{skill.name}' declares {skill.operation} "
            f"but transitively performs {actual}"
        )
```

## Confirmation Points

WRITE operations pause for user confirmation:

```
1. Agent proposes: "Execute skill 'deploy-production' (WRITE)"
2. User sees: Summary of what will be modified
3. User confirms or denies
4. On confirm: Execution proceeds
5. On deny: Workflow stops gracefully
```

### Confirmation Context

```python
@dataclass
class ConfirmationRequest:
    skill_name: str
    operation: str  # WRITE
    summary: str    # Human-readable description
    affected_resources: List[str]
    estimated_impact: str
    reversible: bool
```

### Batched Confirmations

For chains with multiple WRITE operations:

```yaml
confirmation_mode: BATCH   # Confirm all at once
confirmation_mode: EACH    # Confirm each separately
confirmation_mode: FIRST   # Confirm first WRITE, auto-approve rest
```

## Resource Cleanup

Skills can register cleanup handlers:

```python
@dataclass
class SkillCleanup:
    handler: Callable[[ExecutionContext, Optional[Exception]], None]
    always_run: bool = True  # Run on success AND failure
    order: int = 0           # Lower runs first (stack unwinding)
```

### Cleanup Execution Order

```
skill-a registers cleanup-a
skill-b registers cleanup-b
skill-c registers cleanup-c

On failure at skill-c:
  cleanup-c runs first (reverse order)
  cleanup-b runs second
  cleanup-a runs last
```

### Cleanup Guarantees

1. Cleanup handlers **always run** (even if previous cleanup fails)
2. Cleanup failures are **logged but not thrown**
3. Original error is preserved and re-raised
4. Cleanup receives full context including the error

## Execution Constraints

### Timeouts

```yaml
skill: long-running-task
timeout_ms: 60000  # 60 seconds per skill
```

Chain-level timeout:
```yaml
chain: data-pipeline
timeout_ms: 300000  # 5 minutes for entire chain
```

**Behaviour:**
- On timeout, current skill is cancelled
- Error handling strategy applies
- Partial results may be available

### Resource Limits

```yaml
constraints:
  max_memory_mb: 1024
  max_cpu_percent: 80
  max_network_bytes: 10485760  # 10MB
  max_disk_bytes: 104857600    # 100MB
```

### Recursion Limits

```yaml
constraints:
  max_depth: 10           # Maximum composition depth
  max_iterations: 1000    # For self-recursive skills
```

## Parallel Execution

### Explicit Parallel Blocks

```yaml
composes:
  - step: fetch-all
    parallel:
      - fetch-users
      - fetch-products
      - fetch-analytics
  - step: merge
    inputs:
      users: ${fetch-users.output}
      products: ${fetch-products.output}
      analytics: ${fetch-analytics.output}
```

### Parallel Semantics

1. All parallel skills start simultaneously
2. Execution waits for **all** to complete
3. Errors: fail-fast (one failure stops all) or collect-all
4. Outputs merged into single context

### Race Semantics

```yaml
composes:
  - step: fast-lookup
    race:
      - cache-lookup    # Returns immediately if hit
      - database-lookup # Slower fallback
    timeout_ms: 5000
```

First successful result wins, others are cancelled.

## Observability Integration

### Automatic Tracing

```
[Trace: chain-execution]
├── [Span: fetch-data] duration=150ms, status=ok
├── [Span: transform] duration=80ms, status=ok
└── [Span: save-data] duration=200ms, status=ok
```

### Automatic Metrics

```
skill_execution_duration_ms{skill="fetch-data"} = 150
skill_execution_count{skill="fetch-data", status="success"} = 1
chain_execution_duration_ms{chain="data-pipeline"} = 430
```

### Automatic Audit

```json
{
  "action": "SKILL_CHAIN_EXECUTE",
  "chain_id": "data-pipeline",
  "user_id": "user-123",
  "skills_executed": ["fetch-data", "transform", "save-data"],
  "duration_ms": 430,
  "status": "SUCCESS",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Transaction Boundaries

### No Implicit Transactions

By default, each skill is independent. Failures leave partial state.

### Explicit Transactions

```yaml
skill: atomic-update
transaction: true
composes:
  - begin-transaction
  - update-record-a
  - update-record-b
  - commit-transaction
on_failure: rollback-transaction
```

### Saga Pattern

For distributed transactions:

```yaml
skill: order-saga
saga:
  steps:
    - skill: reserve-inventory
      compensate: release-inventory
    - skill: charge-payment
      compensate: refund-payment
    - skill: ship-order
      compensate: cancel-shipment
```

## Performance Characteristics

### Validation Overhead

| Operation | Typical Latency |
|-----------|-----------------|
| Type validation | <1ms |
| Contract compatibility | <1ms |
| Circular dependency check | O(n) where n = skills |
| Full chain validation | <10ms for typical chains |

### Optimization Strategies

1. **Compilation:** Pre-validate and cache for hot paths
2. **Lazy validation:** Only validate inputs that arrive
3. **Parallel validation:** Validate independent branches concurrently

## Examples

### Simple Sequential Chain

```yaml
skill: email-digest
composes:
  - fetch-unread-emails
  - extract-summaries
  - generate-digest
  - send-digest
error_handling: STOP
```

### Complex Workflow with Error Handling

```yaml
skill: safe-deployment
composes:
  - step: prepare
    parallel:
      - run-tests
      - build-artifact
      - security-scan
  - step: deploy
    sequential:
      - backup-current
      - deploy-new
      - health-check
error_handling: COMPENSATE
compensation:
  - rollback-deployment
  - restore-backup
  - notify-failure
confirmation_required: true
```

### Self-Recursive Skill

```yaml
skill: process-directory
composes:
  - list-files
  - process-files
  - list-subdirectories
  - for-each: process-directory  # Self-recursion
constraints:
  max_depth: 10
  max_iterations: 10000
```
