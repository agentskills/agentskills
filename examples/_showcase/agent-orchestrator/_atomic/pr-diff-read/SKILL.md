# pr-diff-read

Read the diff and changed files from a pull request.

## Description

Retrieves the actual code changes in a pull request:
- Full unified diff
- List of changed files with status (added, modified, deleted, renamed)
- Per-file patches with line numbers
- Hunk information for targeted comments

Essential for understanding what code changed before providing review feedback.

## Metadata

```yaml
domain: github
level: 1
type: atomic
version: 1.0.0
operation: READ
tags:
  - github
  - pull-request
  - diff
  - code-review
  - git
```

## Input Schema

```yaml
inputSchema:
  type: object
  required:
    - repo
    - pr_number
  properties:
    repo:
      type: string
      description: Repository in owner/repo format
    pr_number:
      type: integer
      description: Pull request number
    file_filter:
      type: string
      description: Glob pattern to filter files (e.g., "*.py", "src/**/*.ts")
    context_lines:
      type: integer
      description: Lines of context around changes
      default: 3
    include_patch:
      type: boolean
      description: Include raw patch content
      default: true
    max_files:
      type: integer
      description: Maximum files to return (for large PRs)
      default: 100
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - files
  properties:
    success:
      type: boolean
    summary:
      type: object
      properties:
        total_files:
          type: integer
        additions:
          type: integer
        deletions:
          type: integer
        files_by_status:
          type: object
          properties:
            added:
              type: integer
            modified:
              type: integer
            deleted:
              type: integer
            renamed:
              type: integer
    files:
      type: array
      items:
        type: object
        properties:
          filename:
            type: string
          status:
            type: string
            enum: [added, modified, deleted, renamed, copied]
          previous_filename:
            type: string
            description: For renamed files
          additions:
            type: integer
          deletions:
            type: integer
          changes:
            type: integer
          patch:
            type: string
            description: Unified diff patch
          hunks:
            type: array
            items:
              type: object
              properties:
                old_start:
                  type: integer
                old_lines:
                  type: integer
                new_start:
                  type: integer
                new_lines:
                  type: integer
                header:
                  type: string
    error:
      type: object
```

## Implementation

### Using gh CLI (Preferred)

```bash
# Get list of changed files with details
gh pr view {pr_number} --repo {repo} --json files

# Get full diff
gh pr diff {pr_number} --repo {repo}

# Get diff for specific file
gh pr diff {pr_number} --repo {repo} -- path/to/file.py
```

### Using GitHub REST API

```bash
# Get files changed
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

# Get raw diff
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3.diff" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
```

### Using GitHub MCP Server

```json
{
  "method": "tools/call",
  "params": {
    "name": "list_pull_request_files",
    "arguments": {
      "owner": "{owner}",
      "repo": "{repo}",
      "pull_number": {pr_number}
    }
  }
}
```

## Parsing Unified Diff

```python
def parse_hunks(patch: str) -> list:
    """Parse unified diff into hunks with line numbers."""
    import re

    hunks = []
    hunk_pattern = r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@(.*)?'

    for match in re.finditer(hunk_pattern, patch):
        hunk = {
            'old_start': int(match.group(1)),
            'old_lines': int(match.group(2) or 1),
            'new_start': int(match.group(3)),
            'new_lines': int(match.group(4) or 1),
            'header': match.group(5).strip() if match.group(5) else ''
        }
        hunks.append(hunk)

    return hunks

def get_line_position(patch: str, target_line: int) -> int:
    """
    Get position in diff for a line number.
    Required for creating inline comments.
    """
    lines = patch.split('\n')
    position = 0
    current_line = 0

    for line in lines:
        position += 1
        if line.startswith('@@'):
            # Parse new hunk start
            match = re.match(r'@@ -\d+,?\d* \+(\d+)', line)
            if match:
                current_line = int(match.group(1)) - 1
        elif not line.startswith('-'):
            current_line += 1
            if current_line == target_line:
                return position

    return -1  # Line not in diff
```

## Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `NOT_FOUND` | PR doesn't exist | Check repo and PR number |
| `DIFF_TOO_LARGE` | Diff exceeds size limit | Use file_filter or reduce scope |
| `BINARY_FILE` | File is binary | Binary files have no patch |

## Examples

### Read Diff with Hunks
```yaml
input:
  repo: "org/project"
  pr_number: 42
  file_filter: "*.py"

output:
  success: true
  summary:
    total_files: 3
    additions: 150
    deletions: 45
    files_by_status:
      added: 1
      modified: 2
      deleted: 0
      renamed: 0
  files:
    - filename: "src/utils.py"
      status: "modified"
      additions: 25
      deletions: 10
      changes: 35
      patch: |
        @@ -10,7 +10,12 @@ def calculate(x, y):
         def helper():
             pass
        -    return x + y
        +    # Improved calculation with validation
        +    if x < 0 or y < 0:
        +        raise ValueError("Negative values not allowed")
        +    result = x + y
        +    logger.info(f"Calculated: {result}")
        +    return result
      hunks:
        - old_start: 10
          old_lines: 7
          new_start: 10
          new_lines: 12
          header: "def calculate(x, y):"
    - filename: "src/new_feature.py"
      status: "added"
      additions: 100
      deletions: 0
      changes: 100
      patch: |
        @@ -0,0 +1,100 @@
        +"""New feature module."""
        +
        +class NewFeature:
        +    ...
```

### Large PR with Filter
```yaml
input:
  repo: "org/monorepo"
  pr_number: 500
  file_filter: "packages/core/**/*.ts"
  max_files: 20

output:
  success: true
  summary:
    total_files: 45  # Total in PR
    # ... filtered results
  files:
    # Only matching files, up to max_files
```
