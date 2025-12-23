---
name: text-grep
description: Search for patterns in files or text using regular expressions. Wraps the grep command. Use when finding lines matching a pattern.
level: 1
operation: READ
license: Apache-2.0
---

# Text Grep

Search for text patterns in files using regular expressions.

## When to Use

Use this skill when:
- Finding all occurrences of a string in files
- Searching code for function calls or variable names
- Filtering log files for specific events
- Extracting lines matching a pattern

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | Yes | Regular expression to search for |
| `path` | string | Yes | File or directory to search |
| `recursive` | boolean | No | Search directories recursively (default: false) |
| `ignore_case` | boolean | No | Case-insensitive matching (default: false) |
| `invert` | boolean | No | Show non-matching lines (default: false) |
| `count_only` | boolean | No | Return only match count (default: false) |
| `context` | integer | No | Lines of context around matches |
| `include` | string | No | Only search files matching pattern (e.g., `*.py`) |
| `exclude` | string | No | Skip files matching pattern |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `matches` | object[] | List of matches with file, line number, content |
| `total_count` | integer | Total number of matching lines |
| `files_searched` | integer | Number of files searched |

## Usage

```
Search for "TODO" in all Python files under src/
```

```
Find lines containing "error" (case-insensitive) in /var/log/app.log with 2 lines of context
```

```
Count occurrences of "import" in the project
```

## Example Response

```json
{
  "matches": [
    {
      "file": "src/main.py",
      "line": 42,
      "content": "# TODO: refactor this function"
    },
    {
      "file": "src/utils.py",
      "line": 17,
      "content": "# TODO: add error handling"
    }
  ],
  "total_count": 2,
  "files_searched": 15
}
```

## Why This Matters for Composition

As a core text search operation, `text-grep` enables code intelligence:
- **code-search** (Level 2) combines file-find + text-grep
- **todo-extract** (Level 2) greps for TODO/FIXME and creates issues
- **log-monitor** (Level 3) watches logs for error patterns

## Notes

- Wraps GNU `grep` / POSIX `grep`
- Pattern syntax is POSIX extended regex by default
- For fixed strings (no regex), pattern is matched literally
- Binary files are skipped unless explicitly included
