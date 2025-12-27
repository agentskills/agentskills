---
name: conflict-detect
description: |
  Detect potential file conflicts before parallel execution. Analyses
  write paths to identify overlapping edits that require isolation.
level: 2
operation: READ
license: Apache-2.0
domain: agent-orchestration
composes:
  - skill-registry-read
---

# Conflict Detect

Detect file conflicts before parallel task execution.

## When to Use

- Planning parallel agent execution
- Evaluating worktree requirements
- Identifying merge risks
- Analysing skill file dependencies
- Scheduling automation tasks

## Composition Graph

```
conflict-detect (Level 2, READ)
└── skill-registry-read    # L1: Get skill write paths
```

## Conflict Types

| Type | Description | Resolution |
|------|-------------|------------|
| `direct_overlap` | Same file path | Worktree isolation |
| `pattern_overlap` | Overlapping globs | Worktree isolation |
| `directory_overlap` | Same directory | Check file patterns |
| `append_safe` | Both append to file | May be safe |
| `section_isolated` | Different file sections | May be safe |

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tasks` | object[] | Yes | Tasks with write_paths |
| `check_read_write` | boolean | No | Also check read/write conflicts |
| `include_patterns` | boolean | No | Expand glob patterns |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `has_conflicts` | boolean | Whether any conflicts detected |
| `conflicts` | object[] | List of detected conflicts |
| `safe_parallel` | string[][] | Groups safe to run together |
| `requires_isolation` | string[] | Tasks needing worktrees |

## Conflict Schema

```json
{
  "type": "pattern_overlap",
  "severity": "high",
  "tasks": ["morning-synthesis", "customer-intel"],
  "paths": {
    "morning-synthesis": "daily/**/*.md",
    "customer-intel": "daily/2025/12/*.md"
  },
  "overlap": "daily/2025/12/*.md",
  "resolution": "worktree_isolation",
  "notes": "Both tasks may update today's daily note"
}
```

## Usage

```
Check for conflicts between morning-synthesis and customer-intel
```

```
Analyse write paths for all scheduled tasks
```

```
Detect overlaps in portfolio rebalance tasks
```

## Example Response

```json
{
  "tasks_analysed": 4,
  "has_conflicts": true,
  "conflicts": [
    {
      "type": "pattern_overlap",
      "severity": "high",
      "tasks": ["morning-synthesis", "customer-intel"],
      "overlap": "daily/**",
      "resolution": "worktree_isolation"
    },
    {
      "type": "append_safe",
      "severity": "low",
      "tasks": ["task-a", "task-b"],
      "overlap": "logs/activity.log",
      "resolution": "append_ok"
    }
  ],
  "safe_parallel": [
    ["customer-a-intel", "customer-b-intel", "customer-c-intel"],
    ["github-status"]
  ],
  "requires_isolation": ["morning-synthesis", "customer-intel"]
}
```

## No Conflicts Example

```json
{
  "tasks_analysed": 3,
  "has_conflicts": false,
  "conflicts": [],
  "safe_parallel": [
    ["customer-a-intel", "customer-b-intel", "customer-c-intel"]
  ],
  "requires_isolation": [],
  "notes": "All tasks have isolated write paths"
}
```

## Path Analysis

```
Task: morning-synthesis
  writes: daily/2025/12/23.md
          .cache/automation-markers/*.done

Task: customer-intel
  writes: daily/2025/12/23.md       ← CONFLICT
          customers/*/README.md
          .cache/automation-markers/*.done   ← CONFLICT (safe: different files)

Conflict Analysis:
  daily/2025/12/23.md → HIGH severity, same file
  .cache/automation-markers/*.done → LOW severity, different files
```

## Resolution Strategies

| Severity | Strategy |
|----------|----------|
| high | Worktree isolation required |
| medium | Consider sequential or isolation |
| low | Often safe to parallel |
| none | Safe to parallel |

## Notes

- Always check before spawning parallel agents
- .cache/** conflicts often safe (different dated files)
- daily/** conflicts usually require isolation
- Consider file append patterns
- Read-write conflicts may be acceptable
