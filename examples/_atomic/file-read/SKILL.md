---
name: file-read
description: Read contents of a file, optionally limiting to first/last N lines. Wraps cat/head/tail commands. Use when you need to view file contents.
level: 1
operation: READ
license: Apache-2.0
---

# File Read

Read the contents of a file.

## When to Use

Use this skill when:
- Viewing configuration file contents
- Reading log files (especially last N lines)
- Extracting text from files for processing
- Checking file contents before modification

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to file to read |
| `head` | integer | No | Read only first N lines |
| `tail` | integer | No | Read only last N lines |
| `follow` | boolean | No | Follow file for new content (like `tail -f`) |
| `encoding` | string | No | Character encoding (default: utf-8) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | File contents |
| `lines` | integer | Number of lines read |
| `size` | integer | File size in bytes |
| `truncated` | boolean | Whether output was truncated |

## Usage

```
Read the contents of /etc/hosts
```

```
Show the last 50 lines of /var/log/syslog
```

```
Read the first 10 lines of README.md
```

## Example Response

```json
{
  "content": "127.0.0.1\tlocalhost\n::1\t\tlocalhost\n",
  "lines": 2,
  "size": 35,
  "truncated": false
}
```

## Why This Matters for Composition

As a fundamental READ operation, `file-read` is used everywhere:
- **config-check** (Level 2) reads config + validates schema
- **log-analyse** (Level 3) reads logs + extracts patterns + alerts

## Notes

- Wraps POSIX `cat`, `head`, `tail` commands
- Binary files may not display correctly
- Large files are truncated; use `head`/`tail` for partial reads
- For structured data (JSON, YAML), consider dedicated parsers
