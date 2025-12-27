---
name: weekly-digest
description: |
  Generate a personalised weekly summary aggregating activity from calendar,
  email, tasks, and code. Identifies wins, blockers, and upcoming priorities.
  Delivers via user's preferred channel.
level: 3
operation: READ
license: Apache-2.0
composes:
  - calendar-read
  - email-search
  - github-activity-read
  - task-list-read
  - slack-message-send
  - email-send
  - notion-page-create
tool_discovery:
  calendar:
    prefer: [google-calendar-read, outlook-calendar-read]
  email:
    prefer: [gmail-search, outlook-search]
  tasks:
    prefer: [todoist-read, asana-read, notion-tasks-read, github-issues-list]
  code:
    prefer: [github-activity-read, gitlab-activity-read]
  delivery:
    prefer: [notion-page-create, email-send, slack-message-send]
---

# Weekly Digest

Generate a comprehensive weekly summary from multiple productivity sources.

## Trigger Phrases

- "Give me my weekly summary"
- "What did I accomplish this week?"
- "Prepare my weekly digest"
- "Weekly review" (can be scheduled)

## Workflow Steps

```
1. DETERMINE TIMEFRAME
       │ Default: Monday 00:00 to now
       │ Or: last 7 days
       │
       ▼
2. AGGREGATE: Fetch from all sources in parallel
       │
       ├── Calendar: meetings attended
       ├── Email: important threads, response stats
       ├── Tasks: completed, added, overdue
       ├── Code: commits, PRs, reviews
       └── Slack: key conversations (optional)
       │
       ▼
3. ANALYSE: Categorise and extract insights
       │
       ├── Wins: completed items, shipped features
       ├── Blockers: overdue, waiting on others
       ├── Time spent: by category/project
       └── Upcoming: next week's priorities
       │
       ▼
4. SYNTHESISE: Generate narrative summary
       │ • Executive summary (3-5 sentences)
       │ • Categorised details
       │ • Suggested focus for next week
       │
       ▼
5. DELIVER: Via preferred channel
       │ Notion page | Email | Slack
       │
       ▼
6. RETURN: Summary + link to full report
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `period` | string | No | Time period: this_week, last_week, custom (default: this_week) |
| `start_date` | string | No | Custom period start (ISO date) |
| `end_date` | string | No | Custom period end (ISO date) |
| `focus_areas` | string[] | No | Filter to specific projects/labels |
| `delivery` | string | No | Delivery method: notion, email, slack, return_only |
| `include_metrics` | boolean | No | Include time/count metrics (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Executive summary paragraph |
| `wins` | object[] | Accomplishments with details |
| `blockers` | object[] | Current blockers and waiting items |
| `metrics` | object | Time spent, counts by category |
| `upcoming` | object[] | Next week priorities |
| `report_url` | string | Link to full report (if delivered) |
| `period` | object | Start and end dates covered |

## Usage

```
Give me my weekly summary
```

```
What did I accomplish last week? Focus on the Legal Engine project
```

```
Prepare my weekly digest and post to #standup channel
```

## Example Response

```json
{
  "summary": "Strong week focused on API development. Shipped 3 PRs, closed 12 tasks, and had 8 meetings. Main blocker is awaiting legal review on the Terms update. Next week: focus on performance testing.",
  "wins": [
    {
      "category": "code",
      "item": "Merged PR #234: API rate limiting",
      "impact": "Prevents abuse, enables enterprise tier"
    },
    {
      "category": "tasks",
      "item": "Completed Q4 planning document",
      "impact": "Unblocks team allocation"
    }
  ],
  "blockers": [
    {
      "item": "Terms of Service update",
      "waiting_on": "Legal team",
      "age_days": 5,
      "escalation": "Follow up recommended"
    }
  ],
  "metrics": {
    "meetings": {"count": 8, "hours": 6.5},
    "deep_work": {"hours": 22},
    "tasks_completed": 12,
    "tasks_added": 8,
    "prs_merged": 3,
    "prs_reviewed": 5,
    "emails_sent": 34,
    "emails_received": 127
  },
  "upcoming": [
    {"item": "Performance testing", "priority": "high"},
    {"item": "Q4 kickoff meeting", "date": "2024-12-30"}
  ],
  "report_url": "https://notion.so/weekly-digest-dec-23",
  "period": {
    "start": "2024-12-16",
    "end": "2024-12-22"
  }
}
```

## Aggregation Sources

| Source | Data Extracted |
|--------|----------------|
| **Calendar** | Meeting count, hours, attendees, recurring vs one-off |
| **Email** | Threads participated, response time, flagged items |
| **Tasks** | Completed, created, overdue, by project/label |
| **GitHub** | Commits, PRs opened/merged/reviewed, issues closed |
| **Slack** | Key threads, mentions, reactions (optional) |

## Why Level 3

This workflow demonstrates:
1. **Parallel aggregation**: Fetches from 5+ sources simultaneously
2. **Cross-source analysis**: Correlates meetings with related tasks/emails
3. **Trend detection**: Compares to previous weeks
4. **Flexible delivery**: Adapts to user's preferred output channel
5. **Scheduling support**: Can run automatically (Sunday evening, Monday morning)

## Composition Graph

```
weekly-digest (L3)
    │
    ├─┬─ [Parallel Fetch]
    │ │
    │ ├── calendar-read (L1) ──────► meetings, hours
    │ ├── email-search (L1) ───────► threads, stats
    │ ├── task-list-read (L1) ─────► completed, pending
    │ ├── github-activity-read (L1) ► commits, PRs
    │ └── slack-search (L1) ───────► mentions (optional)
    │
    ├──► [Categorise & Analyse]
    │     • Wins vs blockers
    │     • Time allocation
    │     • Week-over-week trends
    │
    ├──► [Synthesise Report]
    │     • Executive summary
    │     • Detailed sections
    │     • Recommendations
    │
    └─┬─ [Deliver - Tool Discovery]
      │
      ├── notion-page-create (L1)
      ├── email-send (L1)
      └── slack-message-send (L1)
```

## Notes

- First run may be slower as it establishes baselines
- Respects calendar privacy (busy/free only for shared calendars)
- Email analysis uses threads, not individual messages
- Can be scheduled via cron trigger or manual invocation
- Metrics help identify work pattern improvements
