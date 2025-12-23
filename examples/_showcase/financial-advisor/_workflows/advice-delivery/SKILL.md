---
name: advice-delivery
description: |
  End-to-end advice delivery workflow from analysis through SOA preparation,
  compliance approval, client presentation, and implementation. Ensures best
  interests duty compliance at every step.
level: 3
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - client-data-read
  - portfolio-read
  - risk-profile-assess
  - soa-prepare
  - best-interests-verify
  - compliance-check
  - document-generate
  - meeting-schedule
  - trade-execute
state_machine: true
---

# Advice Delivery

Complete advice delivery from analysis to implementation.

## Trigger Phrases

- "Prepare advice for [client] on [topic]"
- "Develop super consolidation recommendation for [name]"
- "Create investment strategy advice for [client]"

## State Machine

```
┌─────────────────┐
│    INITIATED    │ ← Advice request received
└────────┬────────┘
         │ Scope defined
         ▼
┌─────────────────┐
│    ANALYSIS     │ ← Comprehensive situation analysis
│                 │   Strategy development
└────────┬────────┘
         │ Strategy determined
         ▼
┌─────────────────┐
│   SOA_DRAFTING  │ ← Statement of Advice preparation
│                 │   All sections drafted
└────────┬────────┘
         │ Draft complete
         ▼
┌─────────────────┐
│ COMPLIANCE_     │ ← Best interests verification
│ REVIEW          │   Supervisor sign-off
└────────┬────────┘
         │ Approved (or remediate)
         ▼
┌─────────────────┐
│  PRESENTATION   │ ← Client meeting scheduled
│   SCHEDULED     │   Materials prepared
└────────┬────────┘
         │ Meeting held
         ▼
┌─────────────────┐
│   PRESENTED     │ ← Advice explained to client
│                 │   Questions addressed
└────────┬────────┘
         │ Client decision
         ├── Accepted ──┐
         │              ▼
         │   ┌─────────────────┐
         │   │ IMPLEMENTATION  │ ← Execute recommendations
         │   │                 │   Trade, paperwork
         │   └────────┬────────┘
         │            │ Complete
         │            ▼
         │   ┌─────────────────┐
         │   │   COMPLETE      │ ✓ Advice delivered
         │   └─────────────────┘
         │
         ├── Deferred ──┐
         │              ▼
         │   ┌─────────────────┐
         │   │    ON_HOLD      │ ← Client considering
         │   └─────────────────┘
         │
         └── Declined ──┐
                        ▼
            ┌─────────────────┐
            │   DECLINED      │ ← Document reasons
            └─────────────────┘
```

## Workflow Steps

```
1. INITIATION
   │ • Confirm advice scope
   │ • Verify current data
   │ • Check risk profile currency
   │
   ▼
2. ANALYSIS (2-5 hours)
   │ • Comprehensive situation review
   │ • Identify advice needs
   │ • Research product/strategy options
   │ • Evaluate alternatives
   │ • Select recommended approach
   │
   ▼
3. SOA PREPARATION (2-4 hours)
   │ • Draft all required sections
   │ • Document rationale
   │ • Prepare fee disclosures
   │ • Include risk warnings
   │
   ▼
4. COMPLIANCE REVIEW (1-2 days)
   │ • Best interests verification
   │ • Technical accuracy check
   │ • Supervisor sign-off
   │ • Remediate any issues
   │
   ▼
5. PRESENTATION PREP
   │ • Schedule client meeting
   │ • Prepare presentation materials
   │ • Send SOA to client (if requested)
   │
   ▼
6. CLIENT MEETING (60-90 min)
   │ • Present recommendations
   │ • Explain rationale
   │ • Address questions
   │ • Obtain decision
   │
   ▼
7. IMPLEMENTATION (if accepted)
   │ • Collect signatures
   │ • Execute trades
   │ • Complete paperwork
   │ • Confirm completion
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `advice_type` | string | Yes | Type: investment, super, insurance, estate, tax, comprehensive |
| `scope` | object | Yes | What advice covers/excludes |
| `requested_by` | string | No | Who requested the advice |
| `urgency` | string | No | Urgency: normal, priority |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `advice_id` | string | Advice case identifier |
| `status` | string | Current workflow state |
| `soa_id` | string | Statement of Advice reference |
| `compliance` | object | Compliance verification status |
| `presentation` | object | Meeting details |
| `outcome` | string | Client decision |
| `implementation` | object | Implementation status |
| `timeline` | object[] | Full activity timeline |

## Usage

```
Prepare superannuation consolidation advice for John Smith
```

```
Develop comprehensive retirement strategy for the Henderson family
```

```
Create insurance advice for client C-12345
```

## Example Response

```json
{
  "advice_id": "ADV-2024-001234",
  "client_id": "C-12345",
  "status": "IMPLEMENTATION",
  "advice_type": "superannuation",
  "scope": {
    "included": [
      "Superannuation consolidation",
      "Investment option selection",
      "Insurance within super"
    ],
    "excluded": [
      "Personal insurance",
      "Estate planning",
      "Tax structures"
    ]
  },
  "soa_id": "SOA-2024-001234",
  "analysis": {
    "situation_summary": "Client has 3 super funds totalling $485,000. Primary fund has lowest fees and appropriate investment options.",
    "recommendation_summary": "Consolidate 2 external funds into primary fund. Switch to Growth option.",
    "alternatives_considered": [
      "Retain separate funds - rejected (fee drag)",
      "Consolidate to different fund - rejected (current fund appropriate)",
      "Retain defensive allocation - rejected (capacity for growth)"
    ],
    "estimated_benefit": {
      "annual_fee_savings": 1850,
      "projected_additional_retirement_balance": 45000
    }
  },
  "compliance": {
    "best_interests_verified": true,
    "all_steps_satisfied": true,
    "supervisor_approved": true,
    "approved_by": "Senior Adviser Sarah Jones",
    "approved_date": "2024-12-22"
  },
  "presentation": {
    "scheduled": "2024-12-23T14:00:00",
    "location": "Video call",
    "duration": 60,
    "materials_sent": true
  },
  "outcome": "accepted",
  "client_decision_date": "2024-12-23",
  "implementation": {
    "status": "in_progress",
    "tasks": [
      {
        "task": "Authority to proceed signed",
        "status": "complete",
        "date": "2024-12-23"
      },
      {
        "task": "Rollover forms submitted",
        "status": "complete",
        "date": "2024-12-23"
      },
      {
        "task": "Fund 1 rollover",
        "status": "pending",
        "expected": "2024-12-30"
      },
      {
        "task": "Fund 2 rollover",
        "status": "pending",
        "expected": "2024-12-30"
      },
      {
        "task": "Investment switch",
        "status": "pending",
        "expected": "2025-01-03"
      }
    ],
    "estimated_completion": "2025-01-10"
  },
  "timeline": [
    {"date": "2024-12-18", "event": "initiated", "notes": "Annual review identified consolidation opportunity"},
    {"date": "2024-12-19", "event": "analysis_complete", "notes": "3 funds analysed, recommendation developed"},
    {"date": "2024-12-20", "event": "soa_drafted", "notes": "SOA prepared"},
    {"date": "2024-12-22", "event": "compliance_approved", "notes": "BID verified, supervisor signed off"},
    {"date": "2024-12-23", "event": "presented", "notes": "Client accepted advice"},
    {"date": "2024-12-23", "event": "implementation_started", "notes": "Forms submitted"}
  ],
  "audit_reference": "ADV-2024-001234"
}
```

## Best Interests Checkpoints

| Stage | Check | Gate |
|-------|-------|------|
| Initiation | Risk profile current | Yes |
| Analysis | Alternatives evaluated | Yes |
| SOA draft | All sections complete | Yes |
| Compliance | BID verification passed | Yes |
| Presentation | Client understanding confirmed | Yes |
| Implementation | Authority to proceed signed | Yes |

## Timeline Expectations

| Stage | Typical Duration |
|-------|-----------------|
| Initiation | 1 day |
| Analysis | 2-5 days |
| SOA preparation | 2-4 days |
| Compliance review | 1-2 days |
| Presentation scheduling | 3-7 days |
| Implementation | 5-20 days |
| **Total** | **2-6 weeks** |

## Notes

- SOA must be provided before implementation
- Client must have reasonable time to consider (5 business days)
- Declined advice requires documentation of reasons
- Implementation only after signed authority
- All stages create audit trail
