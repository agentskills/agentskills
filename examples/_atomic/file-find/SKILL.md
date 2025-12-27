---
name: file-find
description: Search for files and directories by name, type, size, or modification time. Wraps the POSIX find command. Use when locating files matching specific criteria.
level: 1
operation: READ
license: Apache-2.0
---

# File Find

Search for files and directories matching specified criteria.

## When to Use

Use this skill when:
- Locating files by name pattern (e.g., all `.log` files)
- Finding files modified within a time range
- Searching for files by size (large files, empty files)
- Listing files of a specific type (directories, symlinks)

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Starting directory for search |
| `name` | string | No | Filename pattern (supports wildcards: `*.txt`, `test*`) |
| `type` | string | No | File type: `f` (file), `d` (directory), `l` (symlink) |
| `size` | string | No | Size filter: `+10M` (>10MB), `-1k` (<1KB), `100c` (100 bytes) |
| `mtime` | string | No | Modified time: `-7` (last 7 days), `+30` (older than 30 days) |
| `maxdepth` | integer | No | Maximum directory depth to search |
| `exec` | string | No | Command to execute on each match (use `{}` for filename) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `files` | string[] | List of matching file paths |
| `count` | integer | Number of matches found |

## Usage

```
Find all Python files in /home/user/projects
```

```
Find files larger than 100MB modified in the last 7 days in /var/log
```

```
Find empty directories in the current project
```

## Example Response

```json
{
  "files": [
    "/home/user/projects/app/main.py",
    "/home/user/projects/app/utils.py",
    "/home/user/projects/tests/test_main.py"
  ],
  "count": 3
}
```

## Why This Matters for Composition

As a foundational READ operation, `file-find` enables file discovery in workflows:
- **code-search** (Level 2) can find + grep for patterns in code
- **cleanup-old-files** (Level 3) can find + delete files by age

## Notes

- Wraps POSIX `find` command
- Pattern matching uses shell glob syntax
- For content search, combine with `text-grep`
- Large directory trees may take time; use `maxdepth` to limit
