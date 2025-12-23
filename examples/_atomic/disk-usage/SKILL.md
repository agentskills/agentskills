---
name: disk-usage
description: Check disk space usage for filesystems and directories. Wraps df and du commands. Use when monitoring storage or finding large directories.
level: 1
operation: READ
license: Apache-2.0
---

# Disk Usage

Check filesystem and directory disk space usage.

## When to Use

Use this skill when:
- Checking available disk space
- Finding which directories are using space
- Monitoring filesystem capacity
- Identifying large files or directories

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | No | Path to check (default: all filesystems) |
| `depth` | integer | No | Directory depth for breakdown (0 = total only) |
| `human_readable` | boolean | No | Format sizes as KB/MB/GB (default: true) |
| `threshold` | string | No | Only show items larger than (e.g., "100M") |
| `sort_by_size` | boolean | No | Sort by size descending (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `filesystems` | object[] | Filesystem usage (if no path specified) |
| `directories` | object[] | Directory breakdown (if path specified) |
| `total` | object | Total usage summary |

Filesystem entry:

| Field | Type | Description |
|-------|------|-------------|
| `mount` | string | Mount point |
| `size` | string | Total size |
| `used` | string | Used space |
| `available` | string | Available space |
| `percent_used` | integer | Usage percentage |

## Usage

```
Check disk space on all mounted filesystems
```

```
Find the largest directories under /home, depth 2
```

```
Show directories larger than 1GB in /var
```

## Example Response

```json
{
  "filesystems": [
    {
      "mount": "/",
      "size": "100G",
      "used": "45G",
      "available": "55G",
      "percent_used": 45
    },
    {
      "mount": "/home",
      "size": "500G",
      "used": "320G",
      "available": "180G",
      "percent_used": 64
    }
  ],
  "total": {
    "total_size": "600G",
    "total_used": "365G"
  }
}
```

## Why This Matters for Composition

As a storage monitoring primitive, `disk-usage` enables capacity planning:
- **storage-alert** (Level 2) checks usage + notifies when threshold reached
- **cleanup-workflow** (Level 3) finds large dirs + identifies old files + cleans

## Notes

- Wraps POSIX `df` and `du` commands
- Directory scans can be slow on large filesystems
- Use `threshold` to filter noise from small directories
- Excludes pseudo-filesystems (proc, sys) by default
