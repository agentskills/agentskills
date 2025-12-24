# pr-comment-create

Create comments on a pull request - general, review, or inline on specific lines.

## Description

Creates different types of comments on a pull request:
- **General comments**: Appear in the conversation thread
- **Review comments**: Inline comments on specific lines of code
- **Review comment replies**: Responses to existing review comments

This skill handles the complexity of GitHub's comment positioning system,
which requires calculating diff positions for inline comments.

## Metadata

```yaml
domain: github
level: 1
type: atomic
version: 1.0.0
operation: WRITE
tags:
  - github
  - pull-request
  - code-review
  - comments
  - git
```

## Input Schema

```yaml
inputSchema:
  type: object
  required:
    - repo
    - pr_number
    - body
    - comment_type
  properties:
    repo:
      type: string
      description: Repository in owner/repo format
    pr_number:
      type: integer
      description: Pull request number
    body:
      type: string
      description: Comment content (supports GitHub Markdown)
    comment_type:
      type: string
      enum: [general, inline, reply]
      description: |
        - general: PR conversation comment
        - inline: Line-specific review comment
        - reply: Reply to existing comment
    # For inline comments
    path:
      type: string
      description: File path for inline comment
    line:
      type: integer
      description: Line number in the NEW version of the file
    side:
      type: string
      enum: [LEFT, RIGHT]
      description: |
        - LEFT: Comment on deleted line (old version)
        - RIGHT: Comment on added/unchanged line (new version)
      default: RIGHT
    start_line:
      type: integer
      description: Start line for multi-line comment
    commit_id:
      type: string
      description: Commit SHA (uses HEAD if not specified)
    # For reply comments
    reply_to_id:
      type: integer
      description: Comment ID to reply to (for reply type)
    # Suggestion format
    suggestion:
      type: string
      description: |
        Code suggestion to replace the commented lines.
        Will be formatted as GitHub suggestion block.
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
  properties:
    success:
      type: boolean
    comment:
      type: object
      properties:
        id:
          type: integer
        html_url:
          type: string
        created_at:
          type: string
        body:
          type: string
    error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: string
```

## Implementation

### General Comment (gh CLI)

```bash
gh pr comment {pr_number} --repo {repo} --body "{body}"
```

### General Comment (REST API)

```bash
curl -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments" \
  -d '{"body": "{body}"}'
```

### Inline Review Comment (REST API)

```bash
# Single line comment
curl -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments" \
  -d '{
    "body": "{body}",
    "commit_id": "{commit_sha}",
    "path": "{file_path}",
    "line": {line_number},
    "side": "RIGHT"
  }'

# Multi-line comment
curl -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments" \
  -d '{
    "body": "{body}",
    "commit_id": "{commit_sha}",
    "path": "{file_path}",
    "start_line": {start_line},
    "line": {end_line},
    "start_side": "RIGHT",
    "side": "RIGHT"
  }'
```

### Reply to Comment (REST API)

```bash
curl -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies" \
  -d '{"body": "{body}"}'
```

### Using GitHub MCP Server

```json
{
  "method": "tools/call",
  "params": {
    "name": "create_pull_request_review_comment",
    "arguments": {
      "owner": "{owner}",
      "repo": "{repo}",
      "pull_number": {pr_number},
      "body": "{body}",
      "commit_id": "{sha}",
      "path": "{file_path}",
      "line": {line}
    }
  }
}
```

## Suggestion Format

GitHub supports inline code suggestions. This skill auto-formats suggestions:

```python
def format_suggestion(body: str, suggestion: str | None) -> str:
    """Format comment with optional code suggestion."""
    if suggestion:
        return f"""{body}

```suggestion
{suggestion}
```"""
    return body
```

When the suggestion is accepted, GitHub automatically:
1. Creates a commit with the change
2. Marks the comment as resolved

## Line Number Positioning

**CRITICAL**: GitHub's inline comment system is complex:

```python
def validate_line_comment(path: str, line: int, diff_files: list) -> tuple[bool, str]:
    """
    Validate that a line can receive an inline comment.

    Rules:
    1. Line must be in the diff (added, removed, or context)
    2. For RIGHT side: line number in new file
    3. For LEFT side: line number in old file
    4. Line must be within a hunk, not just any line
    """
    file_data = next((f for f in diff_files if f['filename'] == path), None)
    if not file_data:
        return False, f"File {path} not in PR diff"

    patch = file_data.get('patch', '')
    if not patch:
        return False, "File has no patch (binary or too large)"

    # Parse hunks to find valid line ranges
    # ... (see pr-diff-read for hunk parsing)

    return True, ""
```

## Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `NOT_FOUND` | PR or file not found | Check repo, PR number, file path |
| `INVALID_LINE` | Line not in diff | Line must be within a diff hunk |
| `STALE_COMMIT` | Commit no longer head | Get fresh commit SHA |
| `COMMENT_NOT_FOUND` | Reply target missing | Check comment ID exists |
| `BODY_TOO_LONG` | Comment exceeds limit | Split into multiple comments |

## Examples

### General Comment
```yaml
input:
  repo: "org/project"
  pr_number: 42
  comment_type: "general"
  body: |
    Thanks for the PR! I have a few suggestions:

    1. Consider adding tests for the edge cases
    2. The error handling could be more robust

    Overall looks good! 👍

output:
  success: true
  comment:
    id: 12345
    html_url: "https://github.com/org/project/pull/42#issuecomment-12345"
    created_at: "2025-12-24T10:30:00Z"
```

### Inline Comment with Suggestion
```yaml
input:
  repo: "org/project"
  pr_number: 42
  comment_type: "inline"
  body: "This could be simplified using a list comprehension"
  path: "src/utils.py"
  line: 25
  side: "RIGHT"
  suggestion: "results = [process(x) for x in items if x.valid]"

output:
  success: true
  comment:
    id: 67890
    html_url: "https://github.com/org/project/pull/42#discussion_r67890"
    body: |
      This could be simplified using a list comprehension

      ```suggestion
      results = [process(x) for x in items if x.valid]
      ```
```

### Multi-line Comment
```yaml
input:
  repo: "org/project"
  pr_number: 42
  comment_type: "inline"
  body: "This entire block should use a context manager for proper cleanup"
  path: "src/handler.py"
  start_line: 45
  line: 52
  side: "RIGHT"

output:
  success: true
  comment:
    id: 11111
    html_url: "https://github.com/org/project/pull/42#discussion_r11111"
```

### Reply to Comment
```yaml
input:
  repo: "org/project"
  pr_number: 42
  comment_type: "reply"
  reply_to_id: 67890
  body: "Good point! I've updated the code as suggested."

output:
  success: true
  comment:
    id: 22222
    html_url: "https://github.com/org/project/pull/42#discussion_r22222"
```

## Best Practices

1. **Be specific**: Reference exact line numbers and code snippets
2. **Use suggestions**: When proposing changes, use suggestion blocks
3. **Group related**: Use multi-line comments for related issues
4. **Reply in thread**: Keep discussions organised by replying to existing threads
5. **Markdown**: Use formatting for readability (code blocks, lists, emphasis)
