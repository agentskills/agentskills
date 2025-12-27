---
name: client-data-update
description: Update client profile data in CRM/database. All changes are audit-logged with reason and timestamp. Used after meetings, reviews, or circumstance changes.
level: 1
operation: WRITE
license: Apache-2.0
domain: financial-advisory
requires_approval: true
tool_discovery:
  crm:
    prefer: [xplan-client-update, iress-client-update, salesforce-contact-update]
    fallback: database-update
---

# Client Data Update

Update client profile data with full audit trail.

## When to Use

Use this skill when:
- Recording changes from client meetings
- Updating financial situation after annual review
- Correcting client details
- Recording life events (marriage, job change, retirement)

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `updates` | object | Yes | Fields to update |
| `reason` | string | Yes | Reason for update (audit requirement) |
| `source` | string | No | Source of information: meeting, phone, email, document |
| `effective_date` | string | No | When change takes effect (default: now) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether update succeeded |
| `client_id` | string | Client identifier |
| `fields_updated` | string[] | List of updated fields |
| `audit_id` | string | Audit log reference |
| `previous_values` | object | Values before update (for rollback) |
| `requires_review` | boolean | Whether changes trigger compliance review |

## Usage

```
Update John Smith's employment - now self-employed earning $200k
```

```
Record that client C-12345 has paid off their mortgage
```

```
Update risk profile for Mary Jones after reassessment meeting
```

## Example Request

```json
{
  "client_id": "C-12345",
  "updates": {
    "personal.employment": {
      "status": "self-employed",
      "occupation": "Consultant",
      "income": 200000
    },
    "financial.income.salary": 200000,
    "financial.income.total": 205000
  },
  "reason": "Client advised of employment change during quarterly call",
  "source": "phone"
}
```

## Example Response

```json
{
  "success": true,
  "client_id": "C-12345",
  "fields_updated": [
    "personal.employment.status",
    "personal.employment.occupation",
    "personal.employment.income",
    "financial.income.salary",
    "financial.income.total"
  ],
  "audit_id": "AUD-2024-12-23-001234",
  "previous_values": {
    "personal.employment.status": "employed",
    "personal.employment.occupation": "Software Engineer",
    "personal.employment.income": 180000
  },
  "requires_review": true,
  "triggered_workflows": [
    "income-change-review",
    "risk-profile-reassess"
  ]
}
```

## Triggerable Events

Certain updates trigger compliance workflows:

| Change Type | Triggered Action |
|-------------|------------------|
| Income change >20% | Risk capacity review |
| Employment status change | Goals reassessment |
| Address change | KYC verification |
| Marital status change | Estate planning review |
| New dependent | Insurance needs analysis |
| Asset change >$100k | Portfolio rebalance check |

## Compliance Notes

- All updates require `reason` field (regulatory requirement)
- Updates create immutable audit log entry
- Previous values stored for 7 years
- Supervisor notified for material changes
- Some fields require supervisor approval before commit

## Approval Requirements

| Field Category | Approval Required |
|----------------|-------------------|
| Contact details | No |
| Financial situation | No (logged) |
| Risk profile | Yes (compliance) |
| Service tier | Yes (supervisor) |
| Fee arrangements | Yes (supervisor) |
| Adviser assignment | Yes (supervisor) |

## Notes

- Bulk updates should be batched for audit clarity
- Changes effective immediately unless `effective_date` specified
- Rollback available within 24 hours via audit reference
- Integration sync may take up to 15 minutes
