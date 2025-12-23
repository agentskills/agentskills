---
name: issue-triage
description: Analyse and categorise a GitHub issue, then apply appropriate labels and assign to the right team member. Use when new issues need classification and routing.
level: 2
operation: WRITE
license: Apache-2.0
composes:
  - github-issues-list
  - github-issues-create
---

# Issue Triage

Analyse a GitHub issue and apply appropriate labels, priority, and assignment.

## When to Use

Use this skill when:
- New issues need classification (bug vs feature vs question)
- Routing issues to the appropriate team member
- Applying priority labels based on content analysis
- Finding duplicate issues before processing

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner |
| `repository` | string | Yes | Repository name |
| `issue_number` | integer | Yes | Issue to triage |
| `label_scheme` | object | No | Custom label mappings |
| `team_routing` | object | No | Team member assignments by area |
| `check_duplicates` | boolean | No | Search for similar issues (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `classification` | object | Issue type, priority, area |
| `labels_applied` | string[] | Labels that were added |
| `assignee` | string | Assigned team member (if any) |
| `duplicates` | object[] | Potential duplicate issues found |
| `triage_notes` | string | Explanation of decisions |

## Usage

```
Triage issue #42 in anthropics/claude-code - classify it, apply labels, and assign to the right person
```

```
Analyse new issues in my-org/my-repo and route bugs to @backend-team, features to @product-team
```

## Example Response

```json
{
  "classification": {
    "type": "bug",
    "priority": "high",
    "area": "parser",
    "complexity": "medium"
  },
  "labels_applied": ["bug", "priority:high", "area:parser"],
  "assignee": "octocat",
  "duplicates": [
    {
      "number": 38,
      "title": "Parser fails on nested brackets",
      "similarity": 0.85
    }
  ],
  "triage_notes": "Classified as high-priority bug affecting parser. Similar to #38 but different root cause. Assigned to @octocat who owns parser code."
}
```

## Why Level 2

This skill combines:
1. `github-issues-list` - Search for duplicates and get context
2. Analysis - Classify issue type, priority, and area
3. Label/assignment logic - Apply team routing rules

The intelligence is in the **analysis layer** between reading and writing.

## Composition Pattern

```
issue-triage
    │
    ├── github-issues-list (find duplicates)
    │       │
    │       ▼
    │   [Analyse & classify]
    │       │
    │       ▼
    └── github-issue-update (labels + assign)
```

## Notes

- Requires write access to apply labels/assignments
- Custom label schemes override defaults
- Duplicate detection uses title + body similarity
- Inspired by n8n GitHub workflows with AI classification
