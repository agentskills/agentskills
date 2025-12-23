---
name: annual-review
description: |
  Conduct annual client review including pre-meeting preparation, review meeting,
  and post-meeting actions. Ensures regulatory compliance and ongoing service delivery.
level: 3
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - client-data-read
  - portfolio-read
  - portfolio-analyse
  - document-generate
  - meeting-schedule
  - client-data-update
  - risk-profile-assess
  - fee-disclosure-prepare
  - compliance-check
state_machine: true
---

# Annual Review

Complete annual client review workflow.

## Trigger Phrases

- "Conduct annual review for [client]"
- "Prepare for review meeting with [name]"
- "Start annual review process for clients due in [month]"

## State Machine

```
┌─────────────────┐
│    SCHEDULED    │ ← Review due, meeting booked
└────────┬────────┘
         │ T-14 days
         ▼
┌─────────────────┐
│  PRE_REVIEW     │ ← Data refresh, reports generated
│                 │   Duration: 2-3 hours prep
└────────┬────────┘
         │ Preparation complete
         ▼
┌─────────────────┐
│ MEETING_READY   │ ← All materials prepared
│                 │   Agenda sent to client
└────────┬────────┘
         │ Meeting conducted
         ▼
┌─────────────────┐
│   IN_MEETING    │ ← Review meeting in progress
│                 │   Duration: 60-90 min
└────────┬────────┘
         │ Meeting concluded
         ▼
┌─────────────────┐
│  POST_REVIEW    │ ← Update records, determine
│                 │   if advice needed
└────────┬────────┘
         │ Documentation complete
         ▼
┌─────────────────┐
│    COMPLETE     │ ✓ Review cycle complete
└─────────────────┘
```

## Workflow Steps

```
PRE-REVIEW (T-14 to T-1 days)
─────────────────────────────
1. Data Refresh
   │ • Update fact-find with any known changes
   │ • Refresh portfolio data
   │ • Check for any communications since last review
   │
   ▼
2. Generate Reports
   │ • Portfolio performance report
   │ • Goal progress analysis
   │ • Fee disclosure (if due)
   │
   ▼
3. Compliance Checks
   │ • Risk profile currency (reassess if >12 months)
   │ • Fee arrangement status
   │ • Opt-in renewal (if applicable)
   │
   ▼
4. Prepare Agenda
   │ • Customise based on client situation
   │ • Include any specific items from last review
   │ • Note discussion points
   │
   ▼
5. Send Pre-Meeting Pack
   │ • Agenda
   │ • Fact-find update form
   │ • Any questions for client

REVIEW MEETING (60-90 min)
──────────────────────────
6. Opening (5 min)
   │ • Welcome and rapport
   │ • Confirm meeting objectives
   │
   ▼
7. State of the Plan (15 min)
   │ • Progress towards goals
   │ • Key achievements
   │ • Areas of concern
   │
   ▼
8. Personal Update (10 min)
   │ • Changes in circumstances
   │ • Health, family, employment
   │ • New goals or concerns
   │
   ▼
9. Portfolio Review (20 min)
   │ • Performance summary
   │ • Asset allocation
   │ • Holdings review
   │ • Rebalancing needs
   │
   ▼
10. Goal Assessment (10 min)
    │ • Review each goal
    │ • Adjust if needed
    │ • New goals to add
    │
    ▼
11. Planning Items (15 min)
    │ • Tax planning
    │ • Estate planning
    │ • Insurance review
    │ • Retirement planning
    │
    ▼
12. Action Items (10 min)
    │ • Summarise actions
    │ • Confirm responsibilities
    │ • Set timelines

POST-REVIEW (T+1 to T+7 days)
─────────────────────────────
13. Update Records
    │ • Client file updates
    │ • Meeting notes
    │ • Fact-find changes
    │
    ▼
14. Determine Advice Needs
    │ • Changes requiring SOA?
    │ • ROA sufficient?
    │ • No formal advice needed?
    │
    ▼
15. Process Fee Disclosure
    │ • FDS if required
    │ • Opt-in if needed
    │
    ▼
16. Send Follow-Up
    │ • Meeting summary
    │ • Action item confirmation
    │ • Next steps
    │
    ▼
17. Schedule Next Review
    │ • Book next annual review
    │ • Any interim check-ins needed
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `meeting_date` | string | No | Scheduled meeting date |
| `review_type` | string | No | Type: annual, semi-annual, ad-hoc |
| `focus_areas` | string[] | No | Specific areas to focus on |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `review_id` | string | Review cycle identifier |
| `status` | string | Current workflow state |
| `meeting` | object | Meeting details |
| `preparation` | object | Pre-meeting prep status |
| `agenda` | object | Meeting agenda |
| `outcomes` | object | Post-meeting outcomes |
| `action_items` | object[] | Actions to be taken |
| `documents` | object[] | Documents generated |
| `next_review` | string | Next review date |

## Usage

```
Conduct annual review for John Smith, meeting scheduled for next Tuesday
```

```
Prepare review materials for all clients with reviews in January
```

```
Complete post-review actions for client C-12345
```

## Example Response

```json
{
  "review_id": "REV-2024-001234",
  "client_id": "C-12345",
  "status": "POST_REVIEW",
  "review_type": "annual",
  "meeting": {
    "date": "2024-12-20",
    "duration": 75,
    "location": "Office - Meeting Room 2",
    "attendees": ["John Smith", "Mary Smith", "Jane Doe (Adviser)"]
  },
  "preparation": {
    "fact_find_updated": true,
    "portfolio_report_generated": true,
    "performance_analysis_complete": true,
    "fee_disclosure_prepared": true,
    "risk_profile_current": true,
    "agenda_sent": true
  },
  "agenda": {
    "items": [
      {"topic": "State of the plan", "duration": 15},
      {"topic": "Personal circumstances update", "duration": 10},
      {"topic": "Portfolio performance", "duration": 20},
      {"topic": "Goal progress - retirement", "duration": 10},
      {"topic": "Tax planning for year-end", "duration": 10},
      {"topic": "Action items", "duration": 10}
    ]
  },
  "outcomes": {
    "circumstances_changed": true,
    "changes": [
      "John received promotion, income increased 15%",
      "Considering property purchase in 12-18 months"
    ],
    "goals_updated": true,
    "goal_changes": [
      "Added property purchase goal",
      "Retirement target unchanged"
    ],
    "advice_required": "ROA",
    "advice_reason": "Rebalancing recommendation, no material strategy change"
  },
  "action_items": [
    {
      "action": "Prepare ROA for rebalancing",
      "owner": "adviser",
      "due": "2024-12-27"
    },
    {
      "action": "Update risk capacity for income change",
      "owner": "adviser",
      "due": "2024-12-23"
    },
    {
      "action": "Model property deposit scenarios",
      "owner": "adviser",
      "due": "2025-01-10"
    },
    {
      "action": "Provide payslip for updated income",
      "owner": "client",
      "due": "2024-12-30"
    }
  ],
  "documents": [
    {"type": "performance_report", "id": "DOC-PERF-001234"},
    {"type": "meeting_notes", "id": "DOC-NOTES-001234"},
    {"type": "fee_disclosure", "id": "FDS-2024-001234"}
  ],
  "next_review": "2025-12-20",
  "audit_reference": "REV-2024-001234"
}
```

## Review Agenda Template

| Item | Duration | Content |
|------|----------|---------|
| Welcome | 5 min | Rapport, objectives |
| State of plan | 15 min | Goal progress, achievements |
| Personal update | 10 min | Circumstances changes |
| Portfolio review | 20 min | Performance, allocation |
| Goal assessment | 10 min | Review, adjust goals |
| Planning items | 15 min | Tax, estate, insurance |
| Actions | 10 min | Summary, next steps |
| **Total** | **85 min** | |

## Advice Determination

| Situation | Documentation |
|-----------|--------------|
| No changes, on track | File note only |
| Minor changes, no strategy change | Record of Advice (ROA) |
| Material changes, strategy change | Statement of Advice (SOA) |
| Product recommendation | SOA required |

## Compliance Notes

- Annual review required for ongoing fee arrangements
- Risk profile reassessment if >12 months old
- Fee disclosure before anniversary
- All meeting notes retained
- Advice determination documented
- Next review must be scheduled
