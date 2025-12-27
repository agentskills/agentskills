---
name: best-interests-verify
description: Verify that advice complies with Best Interests Duty (s961B Corporations Act). Checks all seven steps and documents compliance evidence.
level: 2
operation: READ
license: Apache-2.0
domain: financial-advisory
composes:
  - client-data-read
  - compliance-check
---

# Best Interests Verify

Verify Best Interests Duty compliance for financial advice.

## When to Use

Use this skill when:
- Before finalising any Statement of Advice
- Reviewing advice for compliance sign-off
- Audit of advice quality
- Training and quality assurance

## Regulatory Background

Section 961B of the Corporations Act requires advisers to act in the client's best interests. The "safe harbour" steps provide a framework for demonstrating compliance.

## Workflow Steps

```
1. IDENTIFY OBJECTIVES: s961B(2)(a)
       │
       └── Client's relevant objectives documented
       │
       ▼
2. IDENTIFY NEEDS: s961B(2)(a)
       │
       └── Financial needs identified and documented
       │
       ▼
3. IDENTIFY CIRCUMSTANCES: s961B(2)(a)
       │
       └── Relevant circumstances considered
       │
       ▼
4. SCOPE DETERMINATION: s961B(2)(b)
       │
       └── Subject matter of advice appropriately scoped
       │
       ▼
5. REASONABLE INVESTIGATIONS: s961B(2)(c)
       │
       └── Adequate product/strategy research conducted
       │
       ▼
6. STRATEGY ASSESSMENT: s961B(2)(d)
       │
       └── Strategies assessed and appropriate one selected
       │
       ▼
7. CLIENT PRIORITY: s961B(2)(e)
       │
       └── No conflicting interests prioritised
       │
       ▼
8. APPROPRIATENESS: s961B(2)(f)
       │
       └── Overall advice appropriate for client
       │
       ▼
9. OTHER STEPS: s961B(2)(g)
       │
       └── Any other reasonable steps taken
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `advice_reference` | string | Yes | SOA/ROA document reference |
| `recommendations` | object[] | No | Recommendations to verify (if not in document) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `compliant` | boolean | Overall BID compliance |
| `safe_harbour_met` | boolean | All safe harbour steps satisfied |
| `steps` | object[] | Each step with status and evidence |
| `gaps` | object[] | Compliance gaps identified |
| `remediation` | object[] | Required actions to achieve compliance |
| `confidence` | integer | Confidence score (0-100) |
| `sign_off_ready` | boolean | Ready for compliance approval |

## Safe Harbour Steps

| Step | Requirement | Evidence Required |
|------|-------------|-------------------|
| 1 | Identify objectives | Goals documented in fact-find |
| 2 | Identify needs | Needs analysis on file |
| 3 | Identify circumstances | Current situation documented |
| 4 | Scope appropriately | Scope statement in SOA |
| 5 | Reasonable investigations | Product research file |
| 6 | Assess strategies | Alternatives in SOA |
| 7 | No conflicts priority | Conflicts register checked |
| 8 | Appropriate advice | Risk profile alignment |
| 9 | Other reasonable steps | Additional due diligence |

## Usage

```
Verify best interests duty for SOA-2024-001234
```

```
Check BID compliance for all advice issued to client C-12345
```

```
Run best interests audit for adviser Jane Doe's last 10 SOAs
```

## Example Response

```json
{
  "compliant": true,
  "safe_harbour_met": true,
  "advice_reference": "SOA-2024-12-23-001234",
  "client_id": "C-12345",
  "steps": [
    {
      "step": 1,
      "name": "identify_objectives",
      "status": "pass",
      "evidence": [
        "Retirement income goal of $80,000 p.a. documented",
        "Goal priority ranking completed",
        "Target retirement age 60 confirmed"
      ],
      "source": "Fact-find dated 2024-11-15"
    },
    {
      "step": 2,
      "name": "identify_needs",
      "status": "pass",
      "evidence": [
        "Gap analysis shows $200,000 shortfall at current trajectory",
        "Insurance needs analysis completed",
        "Estate planning needs identified"
      ],
      "source": "Needs analysis document"
    },
    {
      "step": 3,
      "name": "identify_circumstances",
      "status": "pass",
      "evidence": [
        "Current financial position documented",
        "Employment status confirmed",
        "Health status noted"
      ],
      "source": "Fact-find dated 2024-11-15"
    },
    {
      "step": 4,
      "name": "scope_advice",
      "status": "pass",
      "evidence": [
        "Scope limited to superannuation consolidation",
        "Limitations clearly stated (insurance not covered)",
        "Client agreed to scope"
      ],
      "source": "SOA Section 1"
    },
    {
      "step": 5,
      "name": "reasonable_investigations",
      "status": "pass",
      "evidence": [
        "Product comparison of 5 super funds conducted",
        "Fee analysis documented",
        "Investment option comparison on file"
      ],
      "source": "Product research file PRF-2024-001234"
    },
    {
      "step": 6,
      "name": "assess_strategies",
      "status": "pass",
      "evidence": [
        "Three strategies considered",
        "Rationale for selected strategy documented",
        "Reasons for rejecting alternatives stated"
      ],
      "source": "SOA Section 5 - Alternatives"
    },
    {
      "step": 7,
      "name": "no_conflict_priority",
      "status": "pass",
      "evidence": [
        "Conflicts register reviewed",
        "No conflicting interests identified",
        "Product on APL (independent research)"
      ],
      "source": "Conflicts register, APL confirmation"
    },
    {
      "step": 8,
      "name": "appropriate_advice",
      "status": "pass",
      "evidence": [
        "Recommendation aligns with Growth risk profile",
        "Time horizon appropriate",
        "Client capacity confirmed"
      ],
      "source": "Risk profile dated 2024-06-15"
    },
    {
      "step": 9,
      "name": "other_steps",
      "status": "pass",
      "evidence": [
        "Insurance implications assessed",
        "Tax consequences considered",
        "Transition plan appropriate"
      ],
      "source": "SOA Sections 6-7"
    }
  ],
  "gaps": [],
  "remediation": [],
  "confidence": 95,
  "sign_off_ready": true,
  "verification_timestamp": "2024-12-23T14:30:00Z",
  "verified_by": "Compliance system v2.3",
  "audit_reference": "BID-2024-12-23-001234"
}
```

## Non-Compliant Example

```json
{
  "compliant": false,
  "safe_harbour_met": false,
  "steps": [
    {
      "step": 5,
      "name": "reasonable_investigations",
      "status": "fail",
      "evidence": [
        "Only one product option documented"
      ],
      "gap": "Insufficient product comparison - minimum 3 required"
    }
  ],
  "gaps": [
    {
      "step": 5,
      "severity": "high",
      "description": "Insufficient product research",
      "risk": "Cannot demonstrate reasonable investigations"
    }
  ],
  "remediation": [
    {
      "action": "Expand product research to include minimum 3 comparable products",
      "deadline": "Before SOA delivery",
      "assigned_to": "adviser"
    }
  ],
  "sign_off_ready": false
}
```

## Compliance Notes

- All BID verification results logged permanently
- Failed checks block SOA delivery until remediated
- Audit trail of all evidence reviewed
- Supervisor notified of any non-compliance
- Regular sampling for quality assurance
