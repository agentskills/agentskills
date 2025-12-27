---
name: slack-to-issue
description: Monitor Slack channels for bug reports or feature requests and automatically create GitHub issues. Includes deduplication, classification, and notification back to Slack.
level: 3
operation: WRITE
license: Apache-2.0
composes:
  - slack-message-read
  - github-issues-list
  - github-issues-create
  - slack-message-send
  - issue-triage
---

# Slack to Issue

Convert Slack messages into tracked GitHub issues with full workflow automation.

## When to Use

Use this skill when:
- Team reports bugs in Slack that need GitHub tracking
- Feature requests come through chat channels
- You want automated issue creation from specific Slack triggers
- Ensuring nothing falls through the cracks between chat and issue tracker

## Workflow Steps

```
1. TRIGGER: New message in monitored channel
       │
       ▼
2. FILTER: Does message match bug/feature patterns?
       │ No → Skip
       │ Yes ↓
       ▼
3. DEDUPE: Check GitHub for similar existing issues
       │ Duplicate → Comment on existing, notify Slack
       │ New ↓
       ▼
4. CLASSIFY: Determine type, priority, area (via issue-triage)
       │
       ▼
5. CREATE: Open GitHub issue with Slack context
       │
       ▼
6. NOTIFY: Reply in Slack thread with issue link
       │
       ▼
7. ROUTE: Assign to appropriate team member
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `slack_channel` | string | Yes | Channel ID to monitor |
| `github_owner` | string | Yes | Repository owner |
| `github_repo` | string | Yes | Repository name |
| `trigger_patterns` | string[] | No | Regex patterns to match (default: bug/feature keywords) |
| `team_routing` | object | No | Map areas to GitHub usernames |
| `auto_label` | boolean | No | Automatically apply labels (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `processed_count` | integer | Messages analysed |
| `issues_created` | object[] | New issues created |
| `duplicates_found` | object[] | Matched to existing issues |
| `skipped` | integer | Messages that didn't match triggers |

## Usage

```
Monitor #engineering-bugs channel and create issues in anthropics/claude-code for any messages mentioning "bug", "broken", or "not working"
```

```
Watch #product-feedback for feature requests, create issues in my-org/roadmap, and assign UI requests to @design-team
```

## Example Response

```json
{
  "processed_count": 15,
  "issues_created": [
    {
      "slack_ts": "1703012345.123456",
      "issue_number": 234,
      "issue_url": "https://github.com/anthropics/claude-code/issues/234",
      "title": "Parser crashes on files with unicode characters",
      "labels": ["bug", "priority:high", "area:parser"],
      "assignee": "octocat"
    }
  ],
  "duplicates_found": [
    {
      "slack_ts": "1703012400.654321",
      "existing_issue": 198,
      "similarity": 0.92
    }
  ],
  "skipped": 12
}
```

## Why Level 3

This is a **workflow** because it:
1. **Orchestrates multiple skills**: slack-read → issue-triage → github-create → slack-send
2. **Has decision logic**: Filter, dedupe, route decisions at each step
3. **Manages state**: Tracks what's been processed, links Slack ↔ GitHub
4. **Bidirectional**: Reads from Slack, writes to GitHub, notifies back to Slack

## Composition Graph

```
slack-to-issue (Level 3)
    │
    ├── slack-message-read (L1)
    │
    ├── github-issues-list (L1)
    │       │
    │       ▼
    │   [Dedupe logic]
    │
    ├── issue-triage (L2) ◄── Composes a composite!
    │       │
    │       ▼
    │   [Classification]
    │
    ├── github-issues-create (L1)
    │
    └── slack-message-send (L1)
            │
            ▼
        [Notification]
```

## Notes

- Requires both Slack and GitHub authentication
- Consider rate limits on both platforms
- Thread replies are used to avoid channel noise
- Inspired by popular n8n template "Create Jira issues from Slack messages"
