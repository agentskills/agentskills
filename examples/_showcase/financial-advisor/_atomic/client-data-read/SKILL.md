---
name: client-data-read
description: Read client profile data from CRM/database including personal details, financial situation, risk profile, and service history. Core data access primitive for all financial advisory workflows.
level: 1
operation: READ
license: Apache-2.0
domain: financial-advisory
tool_discovery:
  crm:
    prefer: [xplan-client-read, iress-client-read, salesforce-contact-read]
    fallback: database-query
---

# Client Data Read

Retrieve comprehensive client profile data from the advisory CRM.

## When to Use

Use this skill when:
- Starting any client interaction (meeting prep, review)
- Verifying client details before advice delivery
- Checking current circumstances before recommendations
- Populating document templates with client data

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Unique client identifier |
| `sections` | string[] | No | Specific sections: personal, financial, risk, goals, history |
| `include_related` | boolean | No | Include related parties (spouse, dependents) |
| `as_of_date` | string | No | Historical snapshot date (default: current) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `client` | object | Core client profile |
| `personal` | object | Personal and contact details |
| `financial` | object | Financial situation snapshot |
| `risk_profile` | object | Risk tolerance and capacity |
| `goals` | object[] | Financial objectives |
| `service_tier` | string | Service level classification |
| `related_parties` | object[] | Spouse, dependents, entities |
| `last_review` | object | Most recent review summary |

## Client Object Schema

```json
{
  "client_id": "C-12345",
  "type": "individual",
  "status": "active",
  "personal": {
    "title": "Mr",
    "first_name": "John",
    "last_name": "Smith",
    "dob": "1975-03-15",
    "email": "john.smith@email.com",
    "phone": "+61 412 345 678",
    "address": {
      "street": "123 Collins St",
      "city": "Melbourne",
      "state": "VIC",
      "postcode": "3000"
    },
    "employment": {
      "status": "employed",
      "occupation": "Software Engineer",
      "employer": "Tech Corp",
      "income": 180000
    }
  },
  "financial": {
    "assets": {
      "superannuation": 450000,
      "investments": 120000,
      "property": 850000,
      "cash": 45000
    },
    "liabilities": {
      "mortgage": 520000,
      "other": 15000
    },
    "net_worth": 930000,
    "income": {
      "salary": 180000,
      "other": 5000,
      "total": 185000
    },
    "expenses": {
      "annual": 95000
    }
  },
  "risk_profile": {
    "tolerance": "growth",
    "capacity": "high",
    "score": 72,
    "assessed_date": "2024-06-15"
  },
  "goals": [
    {
      "type": "retirement",
      "target_age": 60,
      "target_income": 80000,
      "priority": "high"
    }
  ],
  "service_tier": "premium",
  "adviser": {
    "id": "A-001",
    "name": "Jane Doe"
  }
}
```

## Usage

```
Get full profile for client C-12345
```

```
Retrieve financial situation and risk profile for the Henderson family
```

```
Look up John Smith's goals and last review date
```

## Example Response

```json
{
  "client_id": "C-12345",
  "status": "active",
  "personal": {
    "name": "John Smith",
    "age": 49,
    "email": "john.smith@email.com"
  },
  "financial": {
    "net_worth": 930000,
    "income": 185000
  },
  "risk_profile": {
    "tolerance": "growth",
    "score": 72
  },
  "goals": [
    {"type": "retirement", "target_age": 60}
  ],
  "service_tier": "premium",
  "last_review": {
    "date": "2024-06-15",
    "next_due": "2025-06-15"
  }
}
```

## Compliance Notes

- All data access is logged with timestamp and accessor identity
- Historical queries include audit trail of changes
- PII is encrypted at rest and in transit
- Access restricted by adviser-client relationship

## Notes

- Returns current snapshot unless `as_of_date` specified
- Related parties require client consent flag
- Large client entities may have multiple linked records
- Caches result for session (5 minute TTL)
