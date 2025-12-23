---
name: github-issues-create
description: Create a new issue in a GitHub repository. Use when the user wants to file a bug report, feature request, or track a task.
level: 1
operation: WRITE
license: Apache-2.0
---

# GitHub Issues Create

Create a new issue in a GitHub repository.

## When to Use

Use this skill when:
- Filing a bug report
- Requesting a new feature
- Creating a task to track work
- Documenting a problem for follow-up

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner (user or organisation) |
| `repository` | string | Yes | Repository name |
| `title` | string | Yes | Issue title |
| `body` | string | No | Issue body (markdown supported) |
| `labels` | string[] | No | Labels to apply to the issue |
| `assignees` | string[] | No | GitHub usernames to assign |
| `milestone` | integer | No | Milestone number to associate |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `issue_number` | integer | Created issue number |
| `issue_url` | string | API URL for the issue |
| `html_url` | string | Web URL for the issue |
| `state` | string | Issue state (always "open" for new issues) |

## Usage

```
Create a GitHub issue in anthropics/claude-code titled "Add vim keybindings support" with body "Would love to have vim-style navigation in the CLI" and labels ["enhancement", "good first issue"]
```

## Example Response

```json
{
  "issue_number": 1234,
  "issue_url": "https://api.github.com/repos/anthropics/claude-code/issues/1234",
  "html_url": "https://github.com/anthropics/claude-code/issues/1234",
  "state": "open"
}
```

## Why This Matters for Composition

As a WRITE operation, `github-issues-create` pairs with READ skills for powerful workflows:
- **bug-triage** (Level 2) can search logs + create issues for errors
- **code-review** (Level 3) can create issues for findings during review

## Notes

- Requires GitHub authentication
- Labels and assignees must exist in the repository
- Use markdown in body for formatting
- Inspired by n8n's GitHub node (Issues resource, Create operation)
