---
name: agent-spawn-decide
description: |
  Decide when to use sub-agents for parallel execution. Analyses task
  characteristics to determine if spawning separate agents is beneficial.
level: 2
operation: READ
license: Apache-2.0
domain: agent-orchestration
composes:
  - skill-registry-read
  - skill-graph-query
---

# Agent Spawn Decide

Decide whether to spawn sub-agents for parallel execution.

## When to Use

- Multiple independent tasks identified
- Long-running operations that could parallelise
- Tasks with separate file domains
- Context isolation beneficial
- Catch-up scenarios with multiple missed runs

## Composition Graph

```
agent-spawn-decide (Level 2, READ)
├── skill-registry-read    # L1: Get task requirements
└── skill-graph-query      # L1: Analyse dependencies
```

## Decision Factors

| Factor | Parallel | Sequential | Weight |
|--------|----------|------------|--------|
| File overlap | No overlap | Same files | 0.35 |
| Dependencies | Independent | Dependent | 0.30 |
| Context needs | Fresh context | Shared context | 0.15 |
| Duration | Long-running | Quick | 0.10 |
| Error isolation | Beneficial | Not needed | 0.10 |

## Decision Matrix

```
                    Independent        Dependent
                    ─────────────────────────────
No file overlap  │  PARALLEL          SEQUENTIAL
                 │  (spawn agents)    (chain skills)
─────────────────┼───────────────────────────────
File overlap     │  WORKTREE          SEQUENTIAL
                 │  (isolate first)   (must serialize)
─────────────────┴───────────────────────────────
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tasks` | object[] | Yes | List of tasks to evaluate |
| `available_resources` | object | No | CPU, memory, agent slots |
| `time_budget` | number | No | Maximum total time in minutes |
| `prefer_parallel` | boolean | No | Bias toward parallelisation |

## Task Schema

```json
{
  "name": "customer-a-intel",
  "skill": "customer-intel",
  "parameters": {"customer_id": "A"},
  "expected_duration_mins": 10,
  "write_paths": ["customers/a/**", "daily/**"],
  "read_paths": ["data/hubspot.json"]
}
```

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `decision` | string | parallel, sequential, hybrid |
| `execution_plan` | object | Detailed execution strategy |
| `estimated_duration` | number | Total expected duration |
| `agent_count` | number | Number of agents to spawn |
| `requires_worktrees` | boolean | Whether isolation needed |

## Execution Plan Schema

```json
{
  "decision": "parallel",
  "execution_plan": {
    "batches": [
      {
        "batch_id": 1,
        "strategy": "parallel",
        "tasks": [
          {"name": "customer-a-intel", "agent": 1, "worktree": true},
          {"name": "customer-b-intel", "agent": 2, "worktree": true},
          {"name": "customer-c-intel", "agent": 3, "worktree": true}
        ]
      },
      {
        "batch_id": 2,
        "strategy": "sequential",
        "tasks": [
          {"name": "aggregate-report", "agent": 1, "worktree": false}
        ],
        "depends_on": [1]
      }
    ],
    "merge_order": ["customer-a-intel", "customer-b-intel", "customer-c-intel"]
  },
  "agent_count": 3,
  "requires_worktrees": true,
  "estimated_duration": 12,
  "notes": "Tasks isolated in worktrees due to daily/** overlap"
}
```

## Usage

```
Should I spawn agents for: [customer-a-intel, customer-b-intel, customer-c-intel]?
```

```
Evaluate parallel execution for morning catchup tasks
```

```
Plan execution strategy for portfolio rebalances
```

## Example: Independent Tasks

```json
{
  "tasks": [
    {"name": "customer-a-intel", "write_paths": ["customers/a/**"]},
    {"name": "customer-b-intel", "write_paths": ["customers/b/**"]},
    {"name": "customer-c-intel", "write_paths": ["customers/c/**"]}
  ],
  "decision": "parallel",
  "agent_count": 3,
  "requires_worktrees": false,
  "reasoning": "Tasks have non-overlapping write paths, can run in parallel without isolation"
}
```

## Example: Overlapping Files

```json
{
  "tasks": [
    {"name": "morning-synthesis", "write_paths": ["daily/**"]},
    {"name": "customer-intel", "write_paths": ["daily/**", "customers/**"]}
  ],
  "decision": "parallel",
  "agent_count": 2,
  "requires_worktrees": true,
  "reasoning": "Both tasks write to daily/**, using worktrees for isolation"
}
```

## Example: Sequential Required

```json
{
  "tasks": [
    {"name": "fetch-data", "output": "data.json"},
    {"name": "analyse-data", "input": "data.json"}
  ],
  "decision": "sequential",
  "agent_count": 1,
  "requires_worktrees": false,
  "reasoning": "analyse-data depends on fetch-data output, must run sequentially"
}
```

## Notes

- Default to sequential if uncertain
- Worktrees add ~5 seconds overhead per task
- Maximum recommended parallel agents: 5
- Consider memory and API rate limits
- Hybrid strategies can mix parallel and sequential
