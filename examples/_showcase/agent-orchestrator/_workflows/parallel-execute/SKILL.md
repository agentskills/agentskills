---
name: parallel-execute
description: |
  Orchestrate parallel execution of multiple agents with intelligent task
  distribution, resource management, and result aggregation.
level: 3
operation: WRITE
license: Apache-2.0
domain: agent-orchestration
composes:
  - agent-spawn-decide
  - conflict-detect
  - worktree-isolate
  - agent-session-spawn
  - completion-marker-set
  - parallel-execute      # Self-recursion for nested parallelism
state_machine: true
---

# Parallel Execute

Orchestrate multi-agent parallel execution.

## When to Use

- Multiple independent tasks to execute
- Scheduled automation catch-up
- Batch processing across entities
- Time-constrained multi-step workflows
- Resource-efficient parallel operations

## State Machine

```
┌─────────────────┐
│  TASK_ANALYSIS  │ ← Analyse task characteristics
└────────┬────────┘
         │ Tasks categorised
         ▼
┌─────────────────┐
│  PLAN_STRATEGY  │ ← Determine parallel/sequential
└────────┬────────┘
         │ Strategy decided
         ▼
┌─────────────────┐
│ RESOURCE_ALLOC  │ ← Allocate agents, worktrees
└────────┬────────┘
         │ Resources ready
         ▼
┌─────────────────┐
│  BATCH_SPAWN    │ ← Launch task batches
└────────┬────────┘
         │ Agents running
         ▼
┌─────────────────────────────────┐
│         EXECUTION LOOP          │
│  ┌─────────────────────────┐   │
│  │ Monitor → Check → Next  │   │
│  └─────────────────────────┘   │
│  FOR each batch:               │
│  ├── Wait for completion       │
│  ├── Verify outputs            │
│  ├── Launch next batch         │
│  └── Handle failures           │
└────────┬────────────────────────┘
         │ All batches complete
         ▼
┌─────────────────┐
│   AGGREGATE     │ ← Combine results
└────────┬────────┘
         │ Results merged
         ▼
┌─────────────────┐
│    COMPLETE     │ ✓ All tasks done
└─────────────────┘
```

## Execution Strategies

### Strategy 1: Pure Parallel
All tasks run simultaneously:
```
Time →
Agent 1: [====Task A====]
Agent 2: [====Task B====]
Agent 3: [====Task C====]
         ↓
         [Aggregate]
```

### Strategy 2: Batched Parallel
Tasks grouped into batches:
```
Time →
Batch 1: [Task A] [Task B] [Task C]
                  ↓
Batch 2:          [Task D] [Task E]
                           ↓
Batch 3:                   [Task F]
```

### Strategy 3: Hybrid Pipeline
Mix of parallel and sequential:
```
Time →
[Fetch A] [Fetch B] [Fetch C]  ← Parallel fetch
         ↓
        [Process All]           ← Sequential process
         ↓
[Report A] [Report B] [Report C] ← Parallel report
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tasks` | object[] | Yes | Tasks to execute |
| `max_parallel` | number | No | Max concurrent agents (default: 5) |
| `strategy` | string | No | pure, batched, hybrid (default: batched) |
| `timeout_total` | number | No | Total execution timeout (mins) |
| `fail_fast` | boolean | No | Stop all on first failure |
| `aggregate_results` | boolean | No | Combine task outputs |

## Task Specification

```json
{
  "tasks": [
    {
      "id": "customer-a",
      "skill": "customer-intel",
      "parameters": {"customer_id": "A"},
      "priority": 1,
      "timeout_mins": 15,
      "dependencies": [],
      "expected_outputs": ["customers/a/README.md"]
    },
    {
      "id": "customer-b",
      "skill": "customer-intel",
      "parameters": {"customer_id": "B"},
      "priority": 1,
      "timeout_mins": 15,
      "dependencies": []
    },
    {
      "id": "aggregate-report",
      "skill": "report-generate",
      "parameters": {},
      "priority": 2,
      "dependencies": ["customer-a", "customer-b"]
    }
  ]
}
```

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | completed, partial, failed |
| `results` | object[] | Per-task results |
| `aggregated` | object | Combined results (if requested) |
| `timeline` | object[] | Execution timeline |
| `resource_usage` | object | Agent/worktree utilisation |

## Usage

```
Execute customer-intel for all active customers in parallel
```

```
Run morning automation batch with 3 parallel agents
```

```
Process portfolio rebalances with dependency ordering
```

## Example: Parallel Customer Intel

```json
{
  "tasks": [
    {"id": "customer-a", "skill": "customer-intel", "customer_id": "A"},
    {"id": "customer-b", "skill": "customer-intel", "customer_id": "B"},
    {"id": "customer-c", "skill": "customer-intel", "customer_id": "C"}
  ],
  "max_parallel": 3,
  "strategy": "pure"
}
```

**Execution Timeline:**
```
00:00  TASK_ANALYSIS: 3 tasks, independent, no file conflicts
00:01  PLAN_STRATEGY: Pure parallel, 3 agents
00:02  RESOURCE_ALLOC: Worktrees not needed
00:03  BATCH_SPAWN: Launching 3 agents
       ├── Agent 1: customer-a started
       ├── Agent 2: customer-b started
       └── Agent 3: customer-c started
05:30  customer-b completed (first)
07:15  customer-a completed
08:45  customer-c completed
08:46  AGGREGATE: Combining results
08:47  COMPLETE

Result:
  status: completed
  duration: 8m 47s
  parallel_efficiency: 0.89
```

## Example: Batched with Dependencies

```json
{
  "tasks": [
    {"id": "fetch-data", "skill": "data-fetch"},
    {"id": "fetch-news", "skill": "news-fetch"},
    {"id": "process", "skill": "data-process", "dependencies": ["fetch-data", "fetch-news"]},
    {"id": "report", "skill": "report-generate", "dependencies": ["process"]}
  ],
  "strategy": "hybrid"
}
```

**Execution Timeline:**
```
Batch 1 (parallel): [fetch-data, fetch-news]
         │
         ▼ (wait for both)
Batch 2 (sequential): [process]
         │
         ▼ (wait)
Batch 3 (sequential): [report]
```

## Resource Management

```json
{
  "resource_usage": {
    "peak_agents": 3,
    "peak_worktrees": 3,
    "total_agent_minutes": 24,
    "wall_clock_minutes": 9,
    "parallelism_factor": 2.67,
    "memory_peak_mb": 512
  }
}
```

## Error Handling

### Fail Fast Mode
```json
{
  "fail_fast": true,
  "error": {
    "failed_task": "customer-b",
    "reason": "API rate limit",
    "action": "Killed remaining tasks",
    "tasks_cancelled": ["customer-c"],
    "tasks_completed": ["customer-a"]
  }
}
```

### Graceful Degradation
```json
{
  "fail_fast": false,
  "status": "partial",
  "completed": ["customer-a", "customer-c"],
  "failed": ["customer-b"],
  "failure_reason": {"customer-b": "API timeout"},
  "partial_results": true
}
```

## Self-Recursion Pattern

For deeply nested parallel operations:

```
parallel-execute (top level)
├── batch 1: [task-group-a, task-group-b]
│   ├── task-group-a → parallel-execute (nested)
│   │   ├── subtask-a1
│   │   ├── subtask-a2
│   │   └── subtask-a3
│   └── task-group-b → parallel-execute (nested)
│       ├── subtask-b1
│       └── subtask-b2
└── batch 2: [aggregate-all]
```

## Notes

- Max recursion depth: 3 levels
- Monitor total resource usage
- Consider API rate limits
- Log all spawn/complete events
- Clean up promptly on completion
- Partial results often acceptable
