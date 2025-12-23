---
name: github-issues-list
description: List issues from a GitHub repository with filtering options. Use to find open bugs, track project progress, or search for specific issues.
level: 1
operation: READ
license: Apache-2.0
---

# GitHub Issues List

List and filter issues from a GitHub repository.

## When to Use

Use this skill when:
- Finding open issues in a project
- Searching for issues by label or assignee
- Tracking project progress
- Finding issues you created or are assigned to

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner (user or organisation) |
| `repository` | string | Yes | Repository name |
| `state` | string | No | Filter by state: open, closed, all (default: open) |
| `labels` | string[] | No | Filter by labels |
| `assignee` | string | No | Filter by assignee username |
| `creator` | string | No | Filter by creator username |
| `since` | string | No | Only issues updated after this date (ISO 8601) |
| `sort` | string | No | Sort by: created, updated, comments (default: created) |
| `direction` | string | No | Sort direction: asc, desc (default: desc) |
| `per_page` | integer | No | Results per page (max 100, default: 30) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `issues` | list | List of issue objects |
| `total_count` | integer | Total number of matching issues |

Each issue contains:

| Field | Type | Description |
|-------|------|-------------|
| `number` | integer | Issue number |
| `title` | string | Issue title |
| `state` | string | Issue state (open/closed) |
| `labels` | string[] | Applied labels |
| `assignees` | string[] | Assigned users |
| `created_at` | string | Creation timestamp |
| `html_url` | string | Web URL |

## Usage

```
List open issues in anthropics/claude-code with label "bug"
```

```
Find all issues assigned to @octocat in facebook/react since 2024-01-01
```

## Example Response

```json
{
  "issues": [
    {
      "number": 42,
      "title": "Fix memory leak in parser",
      "state": "open",
      "labels": ["bug", "high-priority"],
      "assignees": ["octocat"],
      "created_at": "2024-12-20T10:30:00Z",
      "html_url": "https://github.com/anthropics/claude-code/issues/42"
    }
  ],
  "total_count": 1
}
```

## Why This Matters for Composition

As a READ operation, `github-issues-list` provides data for higher-level workflows:
- **issue-digest** (Level 2) can list issues + summarise for daily standup
- **project-health** (Level 3) can aggregate issues across multiple repos

## Notes

- Requires GitHub authentication for private repositories
- Results are paginated; use `per_page` and pagination for large result sets
- Inspired by n8n's GitHub node (Issues resource, Get All operation)
