# pr-review-submit

Submit a formal review on a pull request with approval, changes requested, or comment.

## Description

Submits a formal GitHub review which:
- Sets an official review status (APPROVE, REQUEST_CHANGES, COMMENT)
- Can include multiple inline comments atomically
- Appears in the PR's review history
- May be required for merge (if branch protection enabled)

This is different from individual comments - a review is a formal assessment.

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
  - approval
  - git
```

## Input Schema

```yaml
inputSchema:
  type: object
  required:
    - repo
    - pr_number
    - event
  properties:
    repo:
      type: string
      description: Repository in owner/repo format
    pr_number:
      type: integer
      description: Pull request number
    event:
      type: string
      enum: [APPROVE, REQUEST_CHANGES, COMMENT]
      description: |
        - APPROVE: Approve the PR for merging
        - REQUEST_CHANGES: Block merge until changes made
        - COMMENT: Neutral feedback without approval/rejection
    body:
      type: string
      description: |
        Overall review comment (optional for APPROVE, required for REQUEST_CHANGES).
        Summarises the review.
    commit_id:
      type: string
      description: Specific commit to review (uses HEAD if not specified)
    comments:
      type: array
      description: Inline comments to include in this review (atomic submission)
      items:
        type: object
        required:
          - path
          - line
          - body
        properties:
          path:
            type: string
            description: File path
          line:
            type: integer
            description: Line number (in new file for RIGHT side)
          side:
            type: string
            enum: [LEFT, RIGHT]
            default: RIGHT
          start_line:
            type: integer
            description: Start line for multi-line comment
          body:
            type: string
            description: Comment content
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
    review:
      type: object
      properties:
        id:
          type: integer
        html_url:
          type: string
        state:
          type: string
        submitted_at:
          type: string
        user:
          type: string
        body:
          type: string
        comments_count:
          type: integer
    error:
      type: object
```

## Implementation

### Using gh CLI

```bash
# Approve
gh pr review {pr_number} --repo {repo} --approve --body "{body}"

# Request changes
gh pr review {pr_number} --repo {repo} --request-changes --body "{body}"

# Comment only
gh pr review {pr_number} --repo {repo} --comment --body "{body}"
```

### Using REST API

```bash
# Create review with inline comments
curl -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews" \
  -d '{
    "commit_id": "{sha}",
    "body": "{summary}",
    "event": "REQUEST_CHANGES",
    "comments": [
      {
        "path": "src/file.py",
        "line": 25,
        "body": "This needs error handling"
      },
      {
        "path": "src/other.py",
        "start_line": 10,
        "line": 15,
        "body": "This block should use a context manager"
      }
    ]
  }'
```

### Using GitHub MCP Server

```json
{
  "method": "tools/call",
  "params": {
    "name": "create_pull_request_review",
    "arguments": {
      "owner": "{owner}",
      "repo": "{repo}",
      "pull_number": {pr_number},
      "event": "APPROVE",
      "body": "LGTM! Great work on the refactoring."
    }
  }
}
```

## Review States

| Event | Meaning | Effect |
|-------|---------|--------|
| `APPROVE` | Approve for merge | Counts toward required approvals |
| `REQUEST_CHANGES` | Block merge | Must be dismissed or resolved |
| `COMMENT` | Neutral feedback | No effect on merge status |

## Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `NOT_FOUND` | PR doesn't exist | Check repo and PR number |
| `ALREADY_REVIEWED` | Duplicate review | Dismiss previous or use different event |
| `SELF_REVIEW` | Can't approve own PR | Request review from others |
| `INVALID_LINE` | Comment line not in diff | Check line is in diff hunk |
| `BODY_REQUIRED` | REQUEST_CHANGES needs body | Provide explanation |

## Examples

### Simple Approval
```yaml
input:
  repo: "org/project"
  pr_number: 42
  event: "APPROVE"
  body: "LGTM! Code is clean and well-tested."

output:
  success: true
  review:
    id: 98765
    html_url: "https://github.com/org/project/pull/42#pullrequestreview-98765"
    state: "APPROVED"
    submitted_at: "2025-12-24T11:00:00Z"
    user: "reviewer"
    body: "LGTM! Code is clean and well-tested."
    comments_count: 0
```

### Request Changes with Inline Comments
```yaml
input:
  repo: "org/project"
  pr_number: 42
  event: "REQUEST_CHANGES"
  body: |
    Good progress but a few issues to address:

    1. Missing error handling in the API client
    2. Test coverage for edge cases needed
    3. Some security concerns with input validation

    Please address these before we can merge.
  comments:
    - path: "src/api/client.py"
      line: 45
      body: |
        This network call needs try/except handling:

        ```suggestion
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            raise APIError(f"Failed to fetch: {e}")
        ```
    - path: "src/api/client.py"
      line: 78
      body: "Consider adding request timeout to prevent hanging"
    - path: "src/validators.py"
      start_line: 20
      line: 25
      body: |
        This validation is insufficient. User input should be sanitised:

        - Check for SQL injection patterns
        - Validate against allowed character set
        - Limit input length

output:
  success: true
  review:
    id: 98766
    state: "CHANGES_REQUESTED"
    comments_count: 3
```

### Comment-Only Review
```yaml
input:
  repo: "org/project"
  pr_number: 42
  event: "COMMENT"
  body: |
    Interesting approach! A few thoughts:

    - Have you considered using async here?
    - The caching strategy looks solid
    - Might be worth adding metrics

    Not blocking, just food for thought.

output:
  success: true
  review:
    id: 98767
    state: "COMMENTED"
    comments_count: 0
```

## Best Practices

1. **Be constructive**: Frame feedback as suggestions, not demands
2. **Explain why**: Don't just say "fix this" - explain the reasoning
3. **Use suggestions**: Make it easy to accept changes with suggestion blocks
4. **Batch comments**: Submit all feedback in one review, not multiple
5. **Summarise**: Use the body to give an overview, details in inline comments
6. **Be timely**: Review PRs promptly to avoid blocking progress
7. **Acknowledge effort**: Recognise good work, not just problems
