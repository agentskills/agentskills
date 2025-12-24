---
name: worktree-merge
description: Merge changes from an isolated worktree back to the main working directory. Handles conflict detection and resolution strategies.
level: 1
operation: WRITE
license: Apache-2.0
domain: agent-orchestration
tool_discovery:
  git:
    prefer: [git-merge, git-rebase]
    fallback: git-cherry-pick
---

# Worktree Merge

Merge worktree changes back to main working directory.

## When to Use

- Task in worktree has completed successfully
- Changes have been verified and tested
- Ready to integrate work back to main branch
- Need to resolve conflicts from parallel work

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `worktree_path` | string | Yes | Path to worktree to merge |
| `strategy` | string | No | Merge strategy: merge, rebase, squash (default: merge) |
| `verify_outputs` | boolean | No | Verify expected outputs before merge (default: true) |
| `expected_outputs` | string[] | No | Glob patterns for expected output files |
| `conflict_resolution` | string | No | auto, manual, abort (default: manual) |
| `cleanup_after` | boolean | No | Remove worktree after merge (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `merged` | boolean | Whether merge succeeded |
| `commit_sha` | string | Merge commit SHA |
| `files_changed` | string[] | List of files modified |
| `conflicts` | object[] | Any conflicts encountered |
| `worktree_removed` | boolean | Whether worktree was cleaned up |

## Merge Strategies

### merge (default)
Standard git merge with merge commit:
```
main: A---B---C---M
           \     /
worktree:   D---E
```

### rebase
Rebase worktree commits onto main:
```
main: A---B---C---D'---E'
```

### squash
Combine all worktree commits into single commit:
```
main: A---B---C---S (squashed D+E)
```

## Conflict Detection

Before merge, detect potential conflicts:

```json
{
  "conflicts": [
    {
      "file": "daily/2025/12/23.md",
      "type": "both_modified",
      "main_changes": "+5 lines",
      "worktree_changes": "+3 lines",
      "resolution": "manual_required"
    }
  ]
}
```

## Usage

```
Merge customer-a-intel worktree using squash strategy
```

```
Merge and verify that daily note was updated
```

```
Rebase worktree/task-b onto main
```

## Example Response

```json
{
  "merged": true,
  "strategy": "squash",
  "commit_sha": "a1b2c3d",
  "commit_message": "Merge worktree: customer-a-intel\n\nTask: customer-a-intel\nCompleted: 2025-12-23T12:30:00Z\nFiles: 3 changed",
  "files_changed": [
    "daily/2025/12/23.md",
    "customers/acme/README.md",
    ".cache/automation-markers/customer-a-intel-2025-12-23.done"
  ],
  "conflicts": [],
  "worktree_removed": true,
  "branch_deleted": true
}
```

## Verification Before Merge

```yaml
verify_outputs: true
expected_outputs:
  - "daily/**/*.md"                    # Daily note updated
  - ".cache/automation-markers/*.done"  # Completion marker set
  - "customers/*/README.md"             # Customer READMEs updated
```

## Notes

- Always verify outputs before merging
- Conflicts should be resolved in a staging area
- Keep worktree until merge confirmed successful
- Use sequential merges for multiple worktrees to avoid conflicts
