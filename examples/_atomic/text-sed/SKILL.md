---
name: text-sed
description: Stream editor for transforming text with substitution patterns. Wraps the sed command. Use for find-and-replace operations in files or streams.
level: 1
operation: READ
license: Apache-2.0
---

# Text Sed

Transform text using stream editing (substitution, deletion, insertion).

## When to Use

Use this skill when:
- Find and replace text in files
- Deleting lines matching a pattern
- Extracting specific portions of text
- Transforming data formats (e.g., CSV field reordering)

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `expression` | string | Yes | Sed expression (e.g., `s/old/new/g`) |
| `input` | string | Yes | Input file path or text content |
| `in_place` | boolean | No | Modify file in place (default: false) |
| `backup` | string | No | Backup extension when editing in place (e.g., `.bak`) |
| `extended_regex` | boolean | No | Use extended regex syntax (default: false) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `output` | string | Transformed text |
| `changes` | integer | Number of substitutions made |
| `modified` | boolean | Whether in-place file was modified |

## Usage

```
Replace all occurrences of "foo" with "bar" in config.txt
```

```
Delete all blank lines from input.txt
```

```
Extract the second column from a CSV file
```

## Example Response

```json
{
  "output": "Hello bar! Welcome to bar city.",
  "changes": 2,
  "modified": false
}
```

## Common Expressions

| Expression | Description |
|------------|-------------|
| `s/old/new/` | Replace first occurrence per line |
| `s/old/new/g` | Replace all occurrences |
| `s/old/new/i` | Case-insensitive replace |
| `/pattern/d` | Delete lines matching pattern |
| `1,10d` | Delete lines 1-10 |
| `/start/,/end/p` | Print lines between patterns |

## Why This Matters for Composition

As a text transformation primitive, `text-sed` enables data manipulation:
- **config-update** (Level 2) reads config + sed transforms + writes
- **log-sanitise** (Level 2) removes sensitive data from logs
- **batch-rename** (Level 3) finds files + generates new names + renames

## Notes

- Wraps POSIX/GNU `sed`
- Default operation is READ (returns transformed text)
- Use `in_place: true` for WRITE operation (modifies file)
- For complex transformations, consider `text-awk`
