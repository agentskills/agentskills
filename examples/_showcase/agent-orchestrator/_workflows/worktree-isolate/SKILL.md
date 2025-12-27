---
name: worktree-isolate
description: |
  Full git worktree isolation workflow for parallel task execution.
  Creates isolated environments, monitors execution, and safely merges results.
level: 3
operation: WRITE
license: Apache-2.0
domain: agent-orchestration
composes:
  - conflict-detect
  - worktree-create
  - agent-session-spawn
  - completion-marker-set
  - worktree-merge
state_machine: true
---

# Worktree Isolate

Complete worktree isolation workflow for safe parallel execution.

## When to Use

- Multiple agents need to edit potentially overlapping files
- Want guaranteed isolation between parallel tasks
- Need easy rollback of failed tasks
- Running scheduled tasks that modify shared files
- Catch-up scenarios with accumulated missed runs

## State Machine

```
┌─────────────────┐
│  CONFLICT_SCAN  │ ← Analyse task file paths
└────────┬────────┘
         │ Conflicts identified
         ▼
┌─────────────────┐
│ WORKTREE_SETUP  │ ← Create isolated worktrees
└────────┬────────┘
         │ All worktrees ready
         ▼
┌─────────────────┐
│  AGENT_SPAWN    │ ← Launch agents in worktrees
└────────┬────────┘
         │ Agents running
         ▼
┌─────────────────┐
│   MONITORING    │ ← Wait for completion/timeout
│                 │   (poll markers, check status)
└────────┬────────┘
         │ All agents complete
         ▼
┌─────────────────┐
│   VERIFY_ALL    │ ← Verify expected outputs
└────────┬────────┘
         │ Outputs valid
         ▼
┌─────────────────┐
│  MERGE_QUEUE    │ ← Sequential merge to main
└────────┬────────┘
         │ Merges complete
         ▼
┌─────────────────┐
│    CLEANUP      │ ← Remove worktrees, branches
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   COMPLETED     │ ✓ All changes integrated
└─────────────────┘

Exception States:
─────────────────
│  AGENT_FAILED  │ → Rollback worktree
│  MERGE_CONFLICT│ → Human resolution queue
│  TIMEOUT       │ → Kill agents, preserve state
```

## Workflow Detail

```
1. CONFLICT SCAN
   │
   ├── Analyse write paths for all tasks
   ├── Detect overlapping patterns
   ├── Determine isolation requirements
   └── Plan merge order (minimize conflicts)
   │
   ▼
2. WORKTREE SETUP
   │
   FOR each task requiring isolation:
   ├── git worktree add .trees/{task} HEAD
   ├── Create task-specific branch
   ├── Verify worktree is clean
   └── Log worktree path
   │
   ▼
3. AGENT SPAWN
   │
   FOR each worktree:
   ├── Create tmux session
   ├── Split window for monitoring
   ├── Inject task prompt
   ├── Start agent with timeout
   └── Record PID and session
   │
   ▼
4. MONITORING (parallel)
   │
   WHILE any agents running:
   ├── Check completion markers
   ├── Monitor timeout thresholds
   ├── Capture output logs
   └── Handle early failures
   │
   ▼
5. VERIFY OUTPUTS
   │
   FOR each completed task:
   ├── Check expected files exist
   ├── Validate file contents
   ├── Verify marker metadata
   └── Flag verification failures
   │
   ▼
6. MERGE QUEUE (sequential)
   │
   FOR each worktree in merge order:
   ├── Verify main is clean
   ├── Merge worktree branch
   ├── Resolve trivial conflicts
   ├── Commit with task metadata
   └── Handle manual conflicts
   │
   ▼
7. CLEANUP
   │
   FOR each worktree:
   ├── Remove worktree: git worktree remove
   ├── Delete branch: git branch -d
   ├── Clean tmux session
   └── Archive logs
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tasks` | object[] | Yes | Tasks requiring isolation |
| `timeout_mins` | number | No | Per-task timeout (default: 30) |
| `merge_strategy` | string | No | sequential, parallel (default: sequential) |
| `verify_outputs` | boolean | No | Verify before merge (default: true) |
| `cleanup_on_failure` | boolean | No | Remove worktrees on failure (default: false) |

## Task Schema

```json
{
  "name": "customer-intel-a",
  "skill": "customer-intel",
  "parameters": {"customer_id": "A"},
  "prompt_file": "prompts/customer-intel.md",
  "expected_outputs": ["customers/a/README.md", "daily/**/*.md"],
  "timeout_mins": 15
}
```

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | completed, partial, failed |
| `tasks_completed` | number | Successfully merged tasks |
| `tasks_failed` | number | Failed or timed out tasks |
| `merge_commits` | string[] | Merge commit SHAs |
| `duration_total` | number | Total execution time |
| `manual_resolution` | object[] | Tasks requiring human intervention |

## Usage

```
Run customer-intel for all customers in isolated worktrees
```

```
Execute morning catch-up tasks with worktree isolation
```

```
Parallel portfolio rebalance with merge queue
```

## Example Execution

```
worktree-isolate:
│
├── CONFLICT_SCAN
│   ├── customer-a-intel: writes daily/**, customers/a/**
│   ├── customer-b-intel: writes daily/**, customers/b/**
│   └── Overlap: daily/** (requires isolation)
│
├── WORKTREE_SETUP
│   ├── git worktree add .trees/customer-a-intel HEAD
│   ├── git worktree add .trees/customer-b-intel HEAD
│   └── Worktrees ready: 2
│
├── AGENT_SPAWN
│   ├── tmux new-session customer-a-intel
│   ├── tmux new-session customer-b-intel
│   └── Agents running: 2
│
├── MONITORING
│   ├── [00:00] Both agents started
│   ├── [05:32] customer-a-intel: marker created
│   ├── [07:15] customer-b-intel: marker created
│   └── All agents complete
│
├── VERIFY_OUTPUTS
│   ├── customer-a-intel: ✓ customers/a/README.md updated
│   ├── customer-b-intel: ✓ customers/b/README.md updated
│   └── Verification passed
│
├── MERGE_QUEUE
│   ├── Merge customer-a-intel → main (commit: a1b2c3d)
│   ├── Merge customer-b-intel → main (commit: e4f5g6h)
│   └── Merges complete: 2/2
│
└── CLEANUP
    ├── Removed .trees/customer-a-intel
    ├── Removed .trees/customer-b-intel
    └── Sessions cleaned

Result:
  status: completed
  tasks_completed: 2
  tasks_failed: 0
  duration_total: 8 minutes
```

## Error Handling

### Agent Failure
```json
{
  "error": "agent_failed",
  "task": "customer-b-intel",
  "reason": "API timeout",
  "worktree_preserved": true,
  "action": "Manual investigation required",
  "recovery": "Re-run task or inspect .trees/customer-b-intel"
}
```

### Merge Conflict
```json
{
  "error": "merge_conflict",
  "task": "customer-a-intel",
  "files": ["daily/2025/12/23.md"],
  "worktree_preserved": true,
  "action": "Manual resolution required",
  "commands": {
    "view": "git diff main..worktree/customer-a-intel",
    "resolve": "cd .trees/customer-a-intel && git mergetool"
  }
}
```

## Notes

- Worktrees share git object store (efficient)
- Sequential merge prevents cascading conflicts
- Preserve worktrees on failure for debugging
- Clean up promptly after successful merge
- Log all operations for audit trail
