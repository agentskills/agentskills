---
name: risk-profile-assess
description: Comprehensive risk profiling combining questionnaire scoring, capacity analysis, and behavioural assessment to determine appropriate investment risk category.
level: 2
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - client-data-read
  - client-data-update
  - document-generate
---

# Risk Profile Assessment

Conduct comprehensive risk profiling for investment suitability.

## When to Use

Use this skill when:
- Onboarding new clients
- Annual review (mandatory reassessment)
- Material change in circumstances
- Client requests different risk exposure
- Before providing investment advice

## Workflow Steps

```
1. RETRIEVE: Get current client data
       │
       ├── Financial situation
       ├── Investment experience
       └── Current risk profile (if exists)
       │
       ▼
2. ASSESS TOLERANCE: Risk attitude questionnaire
       │
       ├── Investment experience questions
       ├── Reaction to volatility scenarios
       ├── Return expectations
       └── Time horizon preferences
       │
       ▼
3. ASSESS CAPACITY: Objective risk capacity
       │
       ├── Income stability
       ├── Liquidity needs
       ├── Time to goal
       ├── Wealth concentration
       └── Debt levels
       │
       ▼
4. RECONCILE: Combine tolerance and capacity
       │
       ├── If tolerance > capacity → capacity governs
       ├── If capacity > tolerance → discuss with client
       └── Document any override decisions
       │
       ▼
5. CLASSIFY: Determine risk category
       │
       ├── Conservative
       ├── Moderately Conservative
       ├── Balanced
       ├── Growth
       └── High Growth
       │
       ▼
6. DOCUMENT: Generate risk profile document
       │
       ├── Questionnaire responses
       ├── Capacity analysis
       ├── Classification rationale
       └── Client acknowledgment
       │
       ▼
7. UPDATE: Save to client record
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `questionnaire_responses` | object | No | Pre-completed questionnaire (or conduct interactively) |
| `override_reason` | string | No | Reason if overriding assessed profile |
| `interactive` | boolean | No | Conduct questionnaire interactively (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `risk_profile` | object | Complete risk assessment |
| `classification` | string | Risk category assigned |
| `tolerance_score` | integer | Risk tolerance score (0-100) |
| `capacity_score` | integer | Risk capacity score (0-100) |
| `recommended_allocation` | object | Asset allocation guidance |
| `document_id` | string | Generated profile document |
| `requires_discussion` | boolean | If tolerance/capacity mismatch |

## Risk Categories

| Category | Tolerance Score | Growth/Defensive Split | Typical Investor |
|----------|----------------|------------------------|------------------|
| Conservative | 0-20 | 30/70 | Retirees, low loss tolerance |
| Moderately Conservative | 21-40 | 50/50 | Pre-retirees, medium-term |
| Balanced | 41-60 | 60/40 | Accumulators, 5-7 year horizon |
| Growth | 61-80 | 75/25 | Long-term investors |
| High Growth | 81-100 | 90/10 | Young, high capacity, experienced |

## Questionnaire Dimensions

| Dimension | Weight | Assessment Method |
|-----------|--------|-------------------|
| Investment experience | 15% | Years, product types traded |
| Time horizon | 20% | Years until funds needed |
| Loss tolerance | 25% | Reaction to portfolio decline scenarios |
| Return expectations | 15% | Expected returns vs realistic benchmarks |
| Income stability | 15% | Employment security, income sources |
| Liquidity needs | 10% | Upcoming major expenses |

## Usage

```
Assess risk profile for new client John Smith
```

```
Reassess risk profile for C-12345 after job change to self-employment
```

```
Review risk capacity for Mary Jones approaching retirement
```

## Example Response

```json
{
  "risk_profile": {
    "client_id": "C-12345",
    "assessment_date": "2024-12-23",
    "classification": "growth",
    "tolerance": {
      "score": 72,
      "category": "growth",
      "key_factors": [
        "15+ years investment experience",
        "Comfortable with 20% drawdown",
        "10+ year time horizon"
      ]
    },
    "capacity": {
      "score": 68,
      "category": "growth",
      "key_factors": [
        "Stable employment",
        "Low debt ratio",
        "Adequate emergency fund"
      ],
      "constraints": [
        "Home deposit goal in 5 years (10% allocation reserved)"
      ]
    },
    "reconciliation": {
      "aligned": true,
      "notes": "Tolerance and capacity aligned at Growth level"
    }
  },
  "classification": "growth",
  "tolerance_score": 72,
  "capacity_score": 68,
  "recommended_allocation": {
    "australian_equities": 35,
    "international_equities": 30,
    "property": 10,
    "fixed_income": 15,
    "cash": 10
  },
  "document_id": "DOC-2024-12-23-RP-001234",
  "requires_discussion": false,
  "next_review": "2025-12-23",
  "audit_reference": "RP-2024-12-23-001234"
}
```

## Tolerance vs Capacity Conflicts

| Scenario | Resolution | Documentation Required |
|----------|------------|------------------------|
| Tolerance > Capacity | Use capacity (lower) | Explain risk of exceeding capacity |
| Capacity > Tolerance | Use tolerance (lower) | Note opportunity cost, client acknowledgment |
| Client requests override | Document extensively | Signed acknowledgment, supervisor review |

## Compliance Notes

- Risk profile must be reassessed at least annually
- Material life changes trigger reassessment
- Client must sign acknowledgment of risk category
- All questionnaire responses retained
- Override decisions require supervisor approval
- Advice must align with assessed profile
