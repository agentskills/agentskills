---
name: client-onboard
description: |
  Complete client onboarding workflow from discovery meeting through to active status.
  Manages multi-day process with state persistence, compliance checkpoints, and
  document collection. Typical duration: 2-4 weeks.
level: 3
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - meeting-schedule
  - document-generate
  - client-data-update
  - kyc-verify
  - risk-profile-assess
  - compliance-check
state_machine: true
---

# Client Onboard

Complete client onboarding workflow with compliance and documentation.

## Trigger Phrases

- "Start onboarding for new prospect [name]"
- "Begin client intake for [person] referred by [source]"
- "Onboard new client from discovery meeting"

## State Machine

```
┌─────────────────┐
│    PROSPECT     │ ← Initial contact recorded
└────────┬────────┘
         │ Discovery meeting scheduled
         ▼
┌─────────────────┐
│   DISCOVERY     │ ← Meeting held, FSG provided
│                 │   Duration: 20-60 min
└────────┬────────┘
         │ FSG acknowledged, questionnaire sent
         ▼
┌─────────────────┐
│ QUESTIONNAIRE   │ ← Awaiting client response
│   PENDING       │   Timeout: 7 days → reminder
└────────┬────────┘
         │ Questionnaire completed
         ▼
┌─────────────────┐
│  KYC_PENDING    │ ← Identity verification
│                 │   AML/CTF checks
└────────┬────────┘
         │ KYC passed
         ▼
┌─────────────────┐
│ RISK_PROFILING  │ ← Risk tolerance & capacity
│                 │   assessment
└────────┬────────┘
         │ Profile confirmed
         ▼
┌─────────────────┐
│    STRATEGY     │ ← Internal team review
│    MEETING      │   Investment committee
└────────┬────────┘
         │ Strategy approved
         ▼
┌─────────────────┐
│  PRESENTATION   │ ← Formal onboarding meeting
│                 │   Strategy presented
└────────┬────────┘
         │ Client accepts & signs
         ▼
┌─────────────────┐
│ DOCUMENTATION   │ ← Collect signatures
│                 │   Archive all documents
└────────┬────────┘
         │ All docs complete
         ▼
┌─────────────────┐
│     ACTIVE      │ ✓ Client fully onboarded
└─────────────────┘

Exception States:
─────────────────
│  KYC_FAILED    │ → Manual review required
│  WITHDRAWN     │ → Client withdrew
│  ON_HOLD       │ → Paused by request
```

## Workflow Steps

```
1. PROSPECT CREATION
   │ • Create client record
   │ • Record referral source
   │ • Schedule discovery meeting
   │
   ▼
2. DISCOVERY MEETING (20-60 min)
   │ • Introduction and rapport
   │ • Understand situation and goals
   │ • Explain services and approach
   │ • Provide FSG
   │ • Confirm interest to proceed
   │
   ▼
3. QUESTIONNAIRE (within 24h of discovery)
   │ • Send detailed questionnaire
   │ • Collect financial information
   │ • Gather goal details
   │ • Set 7-day follow-up reminder
   │
   ▼
4. KYC VERIFICATION
   │ • Collect identity documents
   │ • Run verification checks
   │ • Sanctions/PEP screening
   │ • AML risk assessment
   │
   ▼
5. RISK PROFILING
   │ • Conduct risk questionnaire
   │ • Assess risk capacity
   │ • Determine appropriate category
   │ • Document and confirm
   │
   ▼
6. STRATEGY MEETING (internal)
   │ • Team review of client situation
   │ • Develop recommended strategy
   │ • Investment committee approval
   │ • Prepare presentation materials
   │
   ▼
7. ONBOARDING MEETING (60-90 min)
   │ • Present recommended strategy
   │ • Explain recommendations
   │ • Address questions
   │ • Collect initial signatures
   │
   ▼
8. DOCUMENTATION
   │ • Complete all required forms
   │ • Client agreement signed
   │ • Fee arrangement confirmed
   │ • Archive all documents
   │
   ▼
9. ACTIVATION
   │ • Update client status to active
   │ • Create service schedule
   │ • Send welcome pack
   │ • Trigger implementation workflow
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prospect_name` | string | Yes | Client name |
| `email` | string | Yes | Client email |
| `phone` | string | No | Client phone |
| `referral_source` | string | No | How client was referred |
| `initial_notes` | string | No | Notes from initial contact |
| `adviser_id` | string | No | Assigned adviser |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `client_id` | string | New client identifier |
| `status` | string | Current workflow state |
| `progress` | object | Completion percentage by stage |
| `next_action` | object | Next required action |
| `blockers` | object[] | Any issues blocking progress |
| `documents` | object[] | Documents generated/collected |
| `timeline` | object[] | Timeline of all activities |
| `estimated_completion` | string | Projected completion date |

## Usage

```
Start onboarding for John Smith, email john@email.com, referred by existing client Mary Jones
```

```
Continue onboarding for prospect P-12345 - questionnaire received
```

```
Check onboarding status for all prospects started this month
```

## Example Response

```json
{
  "client_id": "C-12345",
  "prospect_id": "P-12345",
  "status": "QUESTIONNAIRE_PENDING",
  "progress": {
    "overall": 25,
    "stages": {
      "prospect": "complete",
      "discovery": "complete",
      "questionnaire": "in_progress",
      "kyc": "pending",
      "risk_profile": "pending",
      "strategy": "pending",
      "presentation": "pending",
      "documentation": "pending",
      "activation": "pending"
    }
  },
  "next_action": {
    "action": "await_questionnaire",
    "description": "Waiting for client to complete questionnaire",
    "sent_date": "2024-12-20",
    "due_date": "2024-12-27",
    "reminder_scheduled": "2024-12-25",
    "assigned_to": "system"
  },
  "blockers": [],
  "documents": [
    {
      "type": "fsg",
      "status": "acknowledged",
      "date": "2024-12-20",
      "document_id": "DOC-FSG-001234"
    },
    {
      "type": "questionnaire",
      "status": "sent",
      "date": "2024-12-20",
      "document_id": "DOC-QST-001234"
    }
  ],
  "timeline": [
    {
      "date": "2024-12-18",
      "event": "prospect_created",
      "details": "Referred by Mary Jones"
    },
    {
      "date": "2024-12-20",
      "event": "discovery_meeting",
      "details": "60 min meeting, positive outcome"
    },
    {
      "date": "2024-12-20",
      "event": "fsg_provided",
      "details": "FSG v3.2 provided and acknowledged"
    },
    {
      "date": "2024-12-20",
      "event": "questionnaire_sent",
      "details": "Comprehensive questionnaire emailed"
    }
  ],
  "estimated_completion": "2025-01-10",
  "adviser": {
    "id": "A-001",
    "name": "Jane Doe"
  }
}
```

## Timeout and Escalation Rules

| Stage | Timeout | Action |
|-------|---------|--------|
| Questionnaire pending | 7 days | Send reminder |
| Questionnaire pending | 14 days | Phone follow-up |
| Questionnaire pending | 21 days | Escalate to adviser |
| KYC pending | 5 days | Request documents again |
| Strategy meeting | 10 days | Schedule automatically |
| Documentation | 14 days | Follow-up call |

## Compliance Checkpoints

| Checkpoint | Gate | Blocker if Failed |
|------------|------|-------------------|
| FSG provided | Before questionnaire | Yes |
| KYC verified | Before risk profiling | Yes |
| Risk profile current | Before strategy | Yes |
| Strategy approved | Before presentation | Yes |
| All signatures | Before activation | Yes |

## Documents Collected

| Document | Stage | Required |
|----------|-------|----------|
| FSG acknowledgment | Discovery | Yes |
| Completed questionnaire | Questionnaire | Yes |
| Identity documents | KYC | Yes |
| Risk profile acknowledgment | Risk profiling | Yes |
| Client agreement | Documentation | Yes |
| Fee disclosure consent | Documentation | Yes |
| Authority to proceed | Documentation | Yes |

## Notes

- Workflow persists across sessions (can span weeks)
- All state transitions logged for audit
- Notifications sent at each stage
- Can be paused/resumed at any stage
- Withdrawal requires reason documentation
- Average completion time: 2-4 weeks
