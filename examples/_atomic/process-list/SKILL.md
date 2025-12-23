---
name: process-list
description: List running processes with resource usage information. Wraps ps/top commands. Use when monitoring system processes or finding specific programs.
level: 1
operation: READ
license: Apache-2.0
---

# Process List

List and filter running processes with resource information.

## When to Use

Use this skill when:
- Finding processes by name or command
- Checking CPU/memory usage of running programs
- Identifying processes consuming resources
- Finding process IDs for management

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter` | string | No | Filter by process name or command |
| `user` | string | No | Filter by username |
| `sort_by` | string | No | Sort field: cpu, memory, pid, time (default: cpu) |
| `limit` | integer | No | Maximum number of processes to return |
| `all_users` | boolean | No | Show processes from all users (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `processes` | object[] | List of process information |
| `total_count` | integer | Total matching processes |
| `system_load` | object | Overall CPU/memory statistics |

Each process contains:

| Field | Type | Description |
|-------|------|-------------|
| `pid` | integer | Process ID |
| `user` | string | Owner username |
| `cpu_percent` | float | CPU usage percentage |
| `mem_percent` | float | Memory usage percentage |
| `command` | string | Command line |
| `started` | string | Start time |

## Usage

```
List the top 10 processes by CPU usage
```

```
Find all Python processes and their memory usage
```

```
Show processes owned by user "www-data"
```

## Example Response

```json
{
  "processes": [
    {
      "pid": 1234,
      "user": "root",
      "cpu_percent": 25.5,
      "mem_percent": 2.1,
      "command": "/usr/bin/python3 app.py",
      "started": "Dec 23 09:00"
    }
  ],
  "total_count": 1,
  "system_load": {
    "cpu_percent": 45.2,
    "memory_percent": 68.5
  }
}
```

## Why This Matters for Composition

As a system monitoring primitive, `process-list` enables observability:
- **health-check** (Level 2) checks process exists + port responds
- **resource-alert** (Level 3) monitors + detects high usage + notifies

## Notes

- Wraps `ps`, `top` from procps/procps-ng
- CPU percentage may exceed 100% on multi-core systems
- Process list is a snapshot; use monitoring for continuous tracking
- On containers, may only see container processes
