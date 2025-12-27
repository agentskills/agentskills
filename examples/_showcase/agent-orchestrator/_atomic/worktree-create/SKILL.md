---
name: worktree-create
description: Create an isolated git worktree for parallel task execution. Enables multiple agents to work on the same repository without file conflicts.
level: 1
operation: WRITE
license: Apache-2.0
domain: agent-orchestration
tool_discovery:
  git:
    prefer: [git-worktree]
    fallback: git-clone
---

# Worktree Create

Create an isolated git worktree for parallel execution.

## When to Use

- Multiple agents need to work simultaneously
- Tasks might edit the same files
- Need isolation for speculative changes
- Want easy rollback of experimental work
- Parallel execution of independent subtasks

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_name` | string | Yes | Unique identifier for the worktree |
| `base_ref` | string | No | Git ref to base worktree on (default: HEAD) |
| `branch_name` | string | No | Create new branch (default: auto-generated) |
| `path_prefix` | string | No | Directory prefix (default: .trees/) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `worktree_path` | string | Full path to created worktree |
| `branch` | string | Branch name for this worktree |
| `base_commit` | string | Commit SHA the worktree is based on |
| `created_at` | string | Creation timestamp |

## Directory Structure

```
repository/
├── .trees/                    # Worktree container (gitignored)
│   ├── task-a/               # Isolated worktree for task A
│   │   ├── .git              # Worktree git link
│   │   └── (full repo copy)
│   ├── task-b/               # Isolated worktree for task B
│   │   └── (full repo copy)
│   └── .cleanup-queue/       # Worktrees pending deletion
├── .git/
│   └── worktrees/            # Git's worktree metadata
│       ├── task-a/
│       └── task-b/
└── (main working directory)
```

## Usage

```
Create worktree for customer-a-intel task
```

```
Create worktree based on feature/new-skills branch
```

```
Create isolated workspace for portfolio-rebalance
```

## Example Response

```json
{
  "worktree_path": "/repo/.trees/customer-a-intel",
  "branch": "worktree/customer-a-intel-20251223-1200",
  "base_commit": "f5915d0",
  "created_at": "2025-12-23T12:00:00Z",
  "command_executed": "git worktree add -b worktree/customer-a-intel-20251223-1200 .trees/customer-a-intel HEAD"
}
```

## Cleanup Protocol

Worktrees should be cleaned up after task completion:

```bash
# 1. Move to cleanup queue (for safety)
mv .trees/task-a .trees/.cleanup-queue/task-a

# 2. Remove worktree registration
git worktree remove .trees/.cleanup-queue/task-a

# 3. Delete branch if no longer needed
git branch -d worktree/task-a-*
```

## Notes

- Worktrees share the same .git object store (efficient)
- Each worktree can have different checked-out branches
- Changes in worktrees don't affect main working directory
- Use `worktree-merge` to integrate changes back
- .trees/ directory should be in .gitignore
