# pr-read

Read pull request metadata, status, and context from GitHub.

## Description

Retrieves comprehensive information about a pull request including:
- Basic metadata (title, body, author, state, labels)
- Review status and required checks
- Merge status and conflicts
- Associated issues and references

This skill provides the foundation for understanding a PR before reviewing or acting on it.

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
      examples:
        - "anthropics/claude-code"
        - "microsoft/vscode"
    pr_number:
      type: integer
      description: Pull request number
      examples:
        - 123
        - 456
    include_reviews:
      type: boolean
      description: Include review information
      default: true
    include_checks:
      type: boolean
      description: Include CI check status
      default: true
    include_comments:
      type: boolean
      description: Include comment count and summary
      default: false
```

## Output Schema

```yaml
outputSchema:
  type: object
  required:
    - success
    - pr
  properties:
    success:
      type: boolean
    pr:
      type: object
      properties:
        number:
          type: integer
        title:
          type: string
        body:
          type: string
        state:
          type: string
          enum: [open, closed, merged]
        author:
          type: string
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
        head:
          type: object
          properties:
            ref:
              type: string
            sha:
              type: string
        base:
          type: object
          properties:
            ref:
              type: string
            sha:
              type: string
        labels:
          type: array
          items:
            type: string
        draft:
          type: boolean
        mergeable:
          type: boolean
        mergeable_state:
          type: string
        changed_files:
          type: integer
        additions:
          type: integer
        deletions:
          type: integer
        commits:
          type: integer
    reviews:
      type: array
      items:
        type: object
        properties:
          user:
            type: string
          state:
            type: string
            enum: [APPROVED, CHANGES_REQUESTED, COMMENTED, PENDING]
          submitted_at:
            type: string
    checks:
      type: object
      properties:
        total:
          type: integer
        passed:
          type: integer
        failed:
          type: integer
        pending:
          type: integer
        conclusion:
          type: string
    error:
      type: object
```

## Implementation

### Using gh CLI (Preferred)

```bash
# Get PR metadata
gh pr view {pr_number} --repo {repo} --json \
  number,title,body,state,author,createdAt,updatedAt,\
  headRefName,headRefOid,baseRefName,baseRefOid,\
  labels,isDraft,mergeable,mergeStateStatus,\
  changedFiles,additions,deletions,commits

# Get reviews
gh pr view {pr_number} --repo {repo} --json reviews

# Get check status
gh pr checks {pr_number} --repo {repo} --json name,state,conclusion
```

### Using GitHub REST API

```bash
# PR metadata
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

# Reviews
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

# Check runs
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/commits/{head_sha}/check-runs"
```

### Using GitHub MCP Server

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_pull_request",
    "arguments": {
      "owner": "{owner}",
      "repo": "{repo}",
      "pull_number": {pr_number}
    }
  }
}
```

## Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `NOT_FOUND` | PR doesn't exist | Check repo and PR number |
| `AUTH_FAILED` | Token invalid/missing | Set GITHUB_TOKEN |
| `RATE_LIMITED` | API rate limit hit | Wait or use authenticated requests |
| `REPO_NOT_FOUND` | Repository doesn't exist | Check owner/repo format |

## Examples

### Basic PR Read
```yaml
input:
  repo: "anthropics/claude-code"
  pr_number: 29

output:
  success: true
  pr:
    number: 29
    title: "feat: Add composable skills architecture"
    body: "This PR introduces a three-level skill system..."
    state: "open"
    author: "edu-ap"
    created_at: "2025-12-20T10:30:00Z"
    updated_at: "2025-12-24T15:45:00Z"
    head:
      ref: "feature/composable-skills"
      sha: "abc123"
    base:
      ref: "main"
      sha: "def456"
    labels: ["enhancement", "needs-review"]
    draft: false
    mergeable: true
    mergeable_state: "clean"
    changed_files: 45
    additions: 2500
    deletions: 150
    commits: 12
  reviews:
    - user: "reviewer1"
      state: "APPROVED"
      submitted_at: "2025-12-23T14:00:00Z"
  checks:
    total: 5
    passed: 4
    failed: 0
    pending: 1
    conclusion: "pending"
```

### With Error
```yaml
input:
  repo: "org/nonexistent"
  pr_number: 999

output:
  success: false
  error:
    code: "NOT_FOUND"
    message: "Pull request not found"
```
