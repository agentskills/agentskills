---
name: daily-briefing
description: Generate a comprehensive morning briefing from calendar, email, and research. Use at the start of each day for situational awareness and preparation.
level: 3
operation: READ
composes:
  - calendar-read
  - email-read
  - research
  - customer-intel
license: Apache-2.0
---

# Daily Briefing

Generate a comprehensive morning briefing by orchestrating multiple composite skills with decision logic.

## Why This is a Workflow Skill

This skill **orchestrates** multiple Level 2 composites with **decision logic**:

```
daily-briefing (Level 3)
│
├── calendar-read (Level 1)     → Get today's meetings
│
├── FOR EACH external meeting:
│   ├── customer-intel (Level 2) → Company background, recent activity
│   └── research (Level 2)       → Agenda topics, industry news
│
├── email-read (Level 1)        → Flagged/urgent items
│
└── GENERATE briefing with:
    ├── Meeting preparation summaries
    ├── Customer intelligence
    ├── Action items from email
    └── Recommended priorities
```

**Key characteristics of a Level 3 workflow:**
- Contains **decision logic** (skip intel for internal meetings)
- Has **multiple outputs** (briefing + action items + priorities)
- **Orchestrates** composites, not just combines them
- Runs as a **complete process**, not a single operation

## Composition Graph

```
Level 3: daily-briefing
         │
         ├─────────────────┬──────────────────┐
         ▼                 ▼                  ▼
Level 2: customer-intel   research           [email-search]
         │                 │
         ├────┬────┐      ├────┐
         ▼    ▼    ▼      ▼    ▼
Level 1: hubspot slack   web-   pdf-
         -read -read     search save
```

## When to Use

Use this skill when:
- Starting your workday
- Need comprehensive situational awareness
- Have meetings with external parties
- Want prioritised action items

## Workflow Steps

### 1. Calendar Analysis
```
calendar-read → today's events
├── Identify external meetings (has non-company attendees)
├── Extract agenda topics
└── Note meeting times for scheduling
```

### 2. Meeting Preparation (per external meeting)
```
FOR each external meeting:
├── customer-intel(company) → recent activity, open deals, last contact
├── research(agenda_topics) → relevant industry news, talking points
└── Generate meeting brief
```

### 3. Email Triage
```
email-read(flagged=true, urgent=true)
├── Classify by urgency
├── Extract action items
└── Identify blockers
```

### 4. Synthesis
```
GENERATE briefing:
├── Executive summary
├── Meeting briefs (sorted by time)
├── Action items (sorted by priority)
└── Recommended focus areas
```

## Decision Points

| Condition | Action |
|-----------|--------|
| Internal-only meeting | Skip customer-intel, minimal prep |
| Client presentation | Thorough research depth |
| Urgent email from client | Elevate in priorities |
| No external meetings | Focus on email triage |

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | No | today | Date to generate briefing for |
| `include_research` | boolean | No | `true` | Research agenda topics |
| `research_depth` | string | No | `standard` | Depth for topic research |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `briefing` | string | Full markdown briefing |
| `meetings` | list | Prepared meeting briefs |
| `action_items` | list | Prioritised tasks |
| `priorities` | list | Recommended focus areas |
| `alerts` | list | Urgent items needing attention |

## Example Output Structure

```markdown
# Daily Briefing - 18 December 2025

## Today's Schedule
- 09:00 Client call with Acme Corp (prepared)
- 14:00 Team standup (internal)
- 16:00 Vendor review with TechCo (prepared)

## Meeting Briefs

### Acme Corp (09:00)
**Recent Activity:** Last contact 3 days ago, deal in negotiation stage
**Talking Points:** Q4 delivery timeline, pricing discussion
**Research:** Industry trend towards AI automation relevant to their sector

### TechCo (16:00)
**Recent Activity:** Support ticket raised yesterday
**Talking Points:** Address support issue, discuss renewal
**Research:** Competitor launched similar product last week

## Action Items
1. 🔴 Respond to urgent client email (deadline today)
2. 🟡 Review contract for Acme (before 09:00 call)
3. 🟢 Update project status document

## Recommended Focus
1. Prepare for Acme call - high value deal
2. Resolve TechCo support issue before meeting
```

## Notes

- This is READ-only because it gathers and synthesises, doesn't create
- For briefings that create tasks/notes, operation would be WRITE
- Run time varies based on number of external meetings
- Consider caching customer-intel results for frequent contacts
