---
name: fee-disclosure-prepare
description: Prepare Fee Disclosure Statement (FDS) for ongoing fee arrangements. Includes fee summary, services provided, and opt-in renewal consent.
level: 2
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - client-data-read
  - document-generate
---

# Fee Disclosure Prepare

Prepare annual Fee Disclosure Statement for ongoing fee arrangements.

## When to Use

Use this skill when:
- Annual fee disclosure required (before anniversary)
- New ongoing fee arrangement established
- Fee arrangement renewal (opt-in consent)
- Client requests fee breakdown

## Regulatory Background

For ongoing fee arrangements, advisers must provide clients with:
- **Fee Disclosure Statement (FDS)**: Annual summary of fees paid and services received
- **Renewal Notice**: If arrangement started before 1 July 2013, client must actively opt-in to continue

## Workflow Steps

```
1. RETRIEVE: Get fee and service data
       │
       ├── Fee arrangement details
       ├── Fees charged in period
       ├── Services provided
       └── Arrangement anniversary date
       │
       ▼
2. CALCULATE: Summarise fees
       │
       ├── Adviser fees
       ├── Platform fees
       ├── Investment fees
       ├── Insurance premiums
       └── Total costs
       │
       ▼
3. DOCUMENT: Record services provided
       │
       ├── Meetings held
       ├── Advice provided
       ├── Portfolio reviews
       ├── Communications sent
       └── Administrative services
       │
       ▼
4. COMPARE: Fee vs service value
       │
       ├── Services received vs promised
       ├── Year-over-year comparison
       └── Upcoming year services
       │
       ▼
5. GENERATE: Create FDS document
       │
       ├── Fee summary
       ├── Services summary
       ├── Renewal consent (if applicable)
       └── Opt-in form
       │
       ▼
6. DELIVER: Send to client
       │
       ├── Before anniversary date
       └── Allow response time for opt-in
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `period_end` | string | No | FDS period end date (default: anniversary) |
| `include_projection` | boolean | No | Include next year fee estimate (default: true) |
| `require_opt_in` | boolean | No | Include opt-in consent (default: based on arrangement) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `fds_id` | string | Fee Disclosure Statement ID |
| `document_url` | string | URL to FDS document |
| `period` | object | Disclosure period dates |
| `fees` | object | Fee summary |
| `services` | object | Services provided summary |
| `renewal` | object | Opt-in renewal details |
| `due_date` | string | Client response required by |
| `sent` | boolean | Whether FDS was sent to client |

## Usage

```
Prepare fee disclosure statement for client C-12345
```

```
Generate FDS for all clients with anniversaries in January
```

```
Create renewal opt-in notice for legacy client Mary Jones
```

## Example Response

```json
{
  "fds_id": "FDS-2024-12-23-001234",
  "document_url": "https://docs.advisory.com/fds/FDS-2024-12-23-001234",
  "client_id": "C-12345",
  "period": {
    "start": "2024-01-01",
    "end": "2024-12-31",
    "anniversary": "2025-01-15"
  },
  "fees": {
    "summary": {
      "adviser_fees": 3500,
      "platform_fees": 1200,
      "investment_fees": 2100,
      "insurance_premiums": 890,
      "total": 7690
    },
    "adviser_fee_breakdown": {
      "service_fee": 2500,
      "advice_fee": 1000,
      "total": 3500,
      "calculation": "0.88% of portfolio value"
    },
    "comparison": {
      "previous_year": 7200,
      "change": 490,
      "change_percent": 6.8,
      "reason": "Portfolio growth increased percentage-based fees"
    }
  },
  "services": {
    "provided": [
      {
        "service": "Annual review meeting",
        "date": "2024-06-15",
        "delivered": true
      },
      {
        "service": "Portfolio performance reports",
        "frequency": "quarterly",
        "count": 4,
        "delivered": true
      },
      {
        "service": "Phone/email support",
        "interactions": 8,
        "delivered": true
      },
      {
        "service": "Strategy review",
        "date": "2024-06-15",
        "delivered": true
      }
    ],
    "promised": [
      "Annual comprehensive review",
      "Quarterly performance reports",
      "Unlimited phone/email access",
      "Strategy review as needed"
    ],
    "compliance": {
      "all_services_delivered": true,
      "exceptions": []
    }
  },
  "next_year": {
    "services_offered": [
      "Annual comprehensive review",
      "Quarterly performance reports",
      "Phone/email support",
      "Ad-hoc strategy meetings as needed"
    ],
    "estimated_fees": {
      "adviser_fees": 3600,
      "platform_fees": 1250,
      "investment_fees": 2200,
      "total": 7050,
      "note": "Excludes insurance premiums, subject to portfolio value"
    }
  },
  "renewal": {
    "required": false,
    "opt_in_needed": false,
    "arrangement_type": "post_FOFA",
    "auto_renews": true
  },
  "due_date": "2025-01-15",
  "sent": true,
  "sent_date": "2024-12-23",
  "delivery_method": "email"
}
```

## Fee Disclosure Requirements

| Component | Required | Details |
|-----------|----------|---------|
| Period | Yes | 12-month disclosure period |
| Fees paid | Yes | All fees actually charged |
| Services received | Yes | What was provided for fees |
| Services to be provided | Yes | What will be provided next year |
| Renewal consent | Conditional | For pre-1 July 2013 arrangements |

## Opt-In Requirements

| Arrangement Start | Opt-In Required | Consequence of No Opt-In |
|-------------------|-----------------|-------------------------|
| Before 1 July 2013 | Yes (every 2 years) | Arrangement terminates |
| After 1 July 2013 | No | Continues automatically |

## Timeline

| Days Before Anniversary | Action |
|------------------------|--------|
| 60 days | Generate FDS |
| 30 days | Send to client |
| 0 days | Must be received by client |
| +30 days (opt-in) | Consent deadline |

## Compliance Notes

- FDS must be provided before anniversary date
- All fees must be disclosed (no hidden charges)
- Services promised must be services delivered
- Failure to provide FDS is regulatory breach
- Opt-in failures terminate fee arrangements
- Records retained for 7 years
