---
name: soa-prepare
description: Prepare a Statement of Advice (SOA) with all regulatory requirements. Includes situation analysis, recommendations, best interests verification, and compliance checks.
level: 2
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - client-data-read
  - portfolio-read
  - compliance-check
  - document-generate
  - best-interests-verify
---

# SOA Prepare

Prepare a compliant Statement of Advice document.

## When to Use

Use this skill when:
- Providing personal financial advice
- Recommending product changes
- Advising on strategy implementation
- Major portfolio restructure
- Any advice requiring formal documentation

## Workflow Steps

```
1. GATHER: Collect all required information
       │
       ├── Client profile and circumstances
       ├── Current portfolio and holdings
       ├── Goals and objectives
       ├── Risk profile (must be current)
       └── Previous advice history
       │
       ▼
2. ANALYSE: Comprehensive situation analysis
       │
       ├── Gap analysis (current vs desired)
       ├── Strategy options evaluation
       ├── Product research and comparison
       └── Cost-benefit analysis
       │
       ▼
3. VERIFY: Best interests duty compliance
       │
       ├── Loyalty (prioritise client)
       ├── Care (diligent investigation)
       ├── Good faith (honest dealing)
       └── Document verification steps
       │
       ▼
4. DRAFT: Generate SOA sections
       │
       ├── Scope of advice
       ├── Your situation
       ├── Recommendations
       ├── Why appropriate (rationale)
       ├── Risks and warnings
       ├── Fees and costs
       ├── Conflicts disclosure
       ├── Product information
       └── Authority to proceed
       │
       ▼
5. REVIEW: Compliance pre-check
       │
       ├── All required sections present
       ├── Disclosures complete
       ├── Risk profile alignment
       └── Fee disclosure accurate
       │
       ▼
6. GENERATE: Create final document
       │
       ├── Apply branding
       ├── Add signature blocks
       └── Prepare for delivery
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `advice_type` | string | Yes | Type: investment, super, insurance, estate, comprehensive |
| `recommendations` | object[] | Yes | List of recommendations to include |
| `scope` | object | No | Scope limitations (what's covered/not covered) |
| `draft` | boolean | No | Generate as draft (default: true) |

## Recommendation Schema

```json
{
  "recommendations": [
    {
      "type": "superannuation_consolidation",
      "description": "Consolidate external super funds into existing fund",
      "products": [
        {
          "action": "retain",
          "product": "Australian Super - Balanced",
          "reason": "Low fees, strong performance, appropriate risk"
        },
        {
          "action": "rollover",
          "product": "Old Employer Fund",
          "amount": 45000,
          "reason": "Higher fees, duplicate insurance, simplification"
        }
      ],
      "benefits": [
        "Estimated fee savings of $450 p.a.",
        "Simplified administration",
        "Single insurance arrangement"
      ],
      "risks": [
        "Loss of existing insurance during transfer",
        "Potential CGT event (none applicable here)"
      ],
      "alternatives_considered": [
        "Retain separate funds - rejected due to fee drag",
        "Consolidate to different fund - rejected, current fund appropriate"
      ]
    }
  ]
}
```

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `soa_id` | string | SOA document identifier |
| `document_url` | string | URL to access SOA |
| `status` | string | Status: draft, pending_review, approved |
| `compliance_checks` | object | Pre-flight compliance verification |
| `best_interests_verified` | boolean | BID compliance confirmed |
| `sections` | object | Status of each required section |
| `warnings` | string[] | Any issues or concerns |
| `next_steps` | string[] | Actions to finalise and deliver |

## Required Sections

| Section | Content | Regulatory Basis |
|---------|---------|------------------|
| Cover | Client name, date, adviser details | s946A |
| Scope | What advice covers and doesn't | s947B(2)(a) |
| Your situation | Objectives, needs, circumstances | s947B(2)(b) |
| Risk profile | Risk tolerance and capacity | s947B(2)(c) |
| Recommendations | Specific advice given | s947B(2)(d) |
| Why appropriate | Rationale and basis for advice | s947B(2)(e) |
| Risks | Significant risks of recommendations | s947B(2)(f) |
| Fees and costs | All applicable fees disclosed | s947B(2)(g) |
| Conflicts | Any conflicts of interest | s947B(2)(h) |
| Products | Product details if recommending | s947C |
| Alternatives | Why alternatives not recommended | Best practice |
| Authority | Signature and consent section | s946A |

## Usage

```
Prepare SOA for John Smith recommending superannuation consolidation
```

```
Generate comprehensive advice SOA for the Henderson family retirement plan
```

```
Create insurance advice SOA for Sarah Chen
```

## Example Response

```json
{
  "soa_id": "SOA-2024-12-23-001234",
  "document_url": "https://docs.advisory.com/soa/SOA-2024-12-23-001234",
  "status": "pending_review",
  "client_id": "C-12345",
  "advice_type": "superannuation",
  "compliance_checks": {
    "risk_profile_current": true,
    "all_sections_complete": true,
    "fees_accurate": true,
    "products_on_apl": true,
    "conflicts_disclosed": true,
    "best_interests_statement": true
  },
  "best_interests_verified": true,
  "best_interests_evidence": {
    "client_objectives_identified": true,
    "needs_analysis_complete": true,
    "reasonable_investigations": true,
    "alternatives_considered": true,
    "no_conflicting_interests": true
  },
  "sections": {
    "cover": "complete",
    "scope": "complete",
    "situation": "complete",
    "risk_profile": "complete",
    "recommendations": "complete",
    "rationale": "complete",
    "risks": "complete",
    "fees": "complete",
    "conflicts": "complete",
    "products": "complete",
    "authority": "complete"
  },
  "pages": 18,
  "warnings": [],
  "next_steps": [
    "Supervisor review and sign-off",
    "Schedule presentation meeting",
    "Prepare implementation documents"
  ],
  "audit_reference": "SOA-2024-12-23-001234"
}
```

## Compliance Notes

- SOA must be given to client before implementing advice
- Client must have reasonable time to consider (generally 5 business days)
- Signed authority to proceed required before implementation
- Copy retained for 7 years minimum
- Material changes require new SOA or ROA (Record of Advice)
