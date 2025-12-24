---
name: completion-marker-set
description: Set a completion marker to track task execution and enable idempotency. Prevents duplicate runs of scheduled or repeatable tasks.
level: 1
operation: WRITE
license: Apache-2.0
domain: agent-orchestration
---

# Completion Marker Set

Set completion markers for task tracking and idempotency.

## When to Use

- Task has completed successfully
- Need to prevent duplicate execution
- Tracking scheduled task runs
- Recording task metadata for audit
- Enabling catch-up logic for missed runs

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_name` | string | Yes | Name of the completed task |
| `date` | string | No | Date for marker (default: today) |
| `metadata` | object | No | Additional data to store |
| `marker_type` | string | No | done, failed, skipped (default: done) |
| `ttl_days` | number | No | Auto-cleanup after N days |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `marker_path` | string | Path to marker file |
| `created` | boolean | Whether marker was created |
| `already_existed` | boolean | Whether marker already existed |
| `metadata` | object | Stored metadata |

## Marker Types

### done
Task completed successfully:
```
.cache/automation-markers/customer-intel-2025-12-23.done
```

### failed
Task failed with error:
```
.cache/automation-markers/customer-intel-2025-12-23.failed
```

### skipped
Task intentionally skipped:
```
.cache/automation-markers/customer-intel-2025-12-23.skipped
```

## Marker Content Schema

```json
{
  "task": "customer-intel",
  "date": "2025-12-23",
  "completed_at": "2025-12-23T12:30:00Z",
  "duration_seconds": 180,
  "agent_session": "agent-customer-intel-20251223-1200",
  "outputs": [
    "daily/2025/12/23.md",
    "customers/acme/README.md"
  ],
  "metadata": {
    "customers_processed": 5,
    "errors": 0
  }
}
```

## Directory Structure

```
.cache/
├── automation-markers/
│   ├── customer-intel-2025-12-23.done
│   ├── daily-synthesis-2025-12-23.done
│   ├── workspace-sync-2025-12-22.done
│   └── github-status-2025-12-23.failed
└── agent-status/
    ├── customer-intel.completed
    └── github-status.failed
```

## Usage

```
Mark customer-intel task as completed for today
```

```
Set failed marker with error details
```

```
Check if daily-synthesis has run today
```

## Example Response

```json
{
  "marker_path": ".cache/automation-markers/customer-intel-2025-12-23.done",
  "created": true,
  "already_existed": false,
  "marker_type": "done",
  "metadata": {
    "task": "customer-intel",
    "date": "2025-12-23",
    "completed_at": "2025-12-23T12:30:00Z",
    "duration_seconds": 180
  }
}
```

## Idempotency Check

Before running a task:

```python
def should_run_task(task_name: str, date: str) -> bool:
    marker = f".cache/automation-markers/{task_name}-{date}.done"
    if os.path.exists(marker):
        return False  # Already ran today
    return True
```

## Catch-Up Logic

For missed scheduled runs:

```python
def find_missed_runs(task_name: str, schedule: str, lookback_days: int = 7):
    missed = []
    for day in past_days(lookback_days):
        if should_have_run(schedule, day):
            marker = f".cache/automation-markers/{task_name}-{day}.done"
            if not os.path.exists(marker):
                missed.append(day)
    return missed
```

## Notes

- Markers are essential for reliable automation
- Check for marker before starting task
- Set marker immediately after successful completion
- Include enough metadata for debugging
- Consider TTL for marker cleanup
