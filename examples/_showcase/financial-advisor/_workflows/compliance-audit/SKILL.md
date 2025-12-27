---
name: compliance-audit
description: |
  Periodic compliance audit workflow for adviser practices. Reviews advice quality,
  documentation, professional development, and regulatory compliance. Generates
  audit report with findings and remediation actions.
level: 3
operation: READ
license: Apache-2.0
domain: financial-advisory
composes:
  - compliance-check
  - client-data-read
  - best-interests-verify
---

# Compliance Audit

Periodic compliance review and audit workflow.

## Trigger Phrases

- "Run compliance audit for [adviser/practice]"
- "Conduct quarterly compliance review"
- "Audit advice files for [period]"

## Workflow Steps

```
1. SCOPE DEFINITION
   │ • Define audit period
   │ • Select sample (random or targeted)
   │ • Identify focus areas
   │
   ▼
2. DATA COLLECTION
   │ • Retrieve advice files
   │ • Gather documentation
   │ • Extract compliance data
   │
   ▼
3. ADVICE QUALITY REVIEW
   │ • Best interests verification
   │ • SOA completeness
   │ • Risk profile alignment
   │ • Product appropriateness
   │
   ▼
4. DOCUMENTATION REVIEW
   │ • File completeness
   │ • Record currency
   │ • Signature verification
   │ • Retention compliance
   │
   ▼
5. PROFESSIONAL STANDARDS
   │ • CPD hours tracking
   │ • Ethics requirements
   │ • Qualifications currency
   │
   ▼
6. REGULATORY COMPLIANCE
   │ • FSG currency
   │ • Fee disclosure compliance
   │ • Opt-in consent status
   │ • Conflicts register
   │
   ▼
7. FINDINGS ANALYSIS
   │ • Categorise issues
   │ • Assess severity
   │ • Identify patterns
   │
   ▼
8. REMEDIATION PLANNING
   │ • Required actions
   │ • Deadlines
   │ • Responsibilities
   │
   ▼
9. REPORT GENERATION
   │ • Executive summary
   │ • Detailed findings
   │ • Remediation plan
   │ • Trend analysis
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scope` | string | Yes | Scope: adviser, practice, specific_files |
| `adviser_id` | string | No | Specific adviser (if scoped) |
| `period_start` | string | Yes | Audit period start |
| `period_end` | string | Yes | Audit period end |
| `sample_size` | integer | No | Number of files to review |
| `focus_areas` | string[] | No | Specific focus: bid, documentation, cpd |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `audit_id` | string | Audit identifier |
| `scope` | object | Audit scope details |
| `summary` | object | Executive summary |
| `findings` | object[] | Detailed findings |
| `statistics` | object | Compliance metrics |
| `remediation` | object[] | Required actions |
| `report_url` | string | Full audit report |

## Usage

```
Run quarterly compliance audit for adviser Jane Doe
```

```
Conduct practice-wide audit for Q4 2024
```

```
Audit all investment advice files from the last 6 months
```

## Example Response

```json
{
  "audit_id": "AUD-2024-Q4-001",
  "scope": {
    "type": "practice",
    "period": {
      "start": "2024-10-01",
      "end": "2024-12-31"
    },
    "files_reviewed": 45,
    "sample_method": "stratified_random",
    "advisers_covered": 5
  },
  "summary": {
    "overall_rating": "satisfactory",
    "score": 87,
    "critical_findings": 0,
    "high_findings": 2,
    "medium_findings": 5,
    "low_findings": 8,
    "key_observations": [
      "Strong best interests compliance across all files",
      "Two instances of incomplete alternatives documentation",
      "CPD tracking improvement opportunity identified"
    ]
  },
  "findings": [
    {
      "id": "F-001",
      "severity": "high",
      "category": "best_interests_duty",
      "description": "Insufficient alternatives considered in 2 SOAs",
      "affected_files": ["SOA-2024-089", "SOA-2024-102"],
      "requirement": "s961B(2)(d) - assess strategies considered",
      "evidence": "Only 1 product option documented, minimum 3 required",
      "remediation_required": true
    },
    {
      "id": "F-002",
      "severity": "high",
      "category": "documentation",
      "description": "Risk profile assessment expired for 1 client",
      "affected_files": ["C-45678"],
      "requirement": "Risk profile must be current within 12 months",
      "evidence": "Last assessment dated 14 months ago",
      "remediation_required": true
    },
    {
      "id": "F-003",
      "severity": "medium",
      "category": "fee_disclosure",
      "description": "3 FDS documents sent after anniversary date",
      "affected_files": ["C-12345", "C-23456", "C-34567"],
      "requirement": "FDS must be provided before anniversary",
      "evidence": "Sent 5-12 days after due date",
      "remediation_required": false
    }
  ],
  "statistics": {
    "advice_quality": {
      "bid_compliance": 95.6,
      "soa_completeness": 97.8,
      "risk_alignment": 100,
      "product_appropriateness": 100
    },
    "documentation": {
      "file_completeness": 93.3,
      "record_currency": 97.8,
      "signature_compliance": 100
    },
    "professional_standards": {
      "cpd_compliance": 100,
      "ethics_hours": 100
    },
    "regulatory": {
      "fsg_currency": 100,
      "fee_disclosure": 93.3,
      "conflicts_register": 100
    }
  },
  "trends": {
    "vs_previous_quarter": {
      "overall_score": "+3 points",
      "critical_findings": "unchanged (0)",
      "improvements": ["SOA completeness", "Record currency"],
      "declines": ["Fee disclosure timeliness"]
    }
  },
  "remediation": [
    {
      "finding_id": "F-001",
      "action": "Re-document alternatives for affected SOAs",
      "owner": "Affected advisers",
      "deadline": "2025-01-15",
      "status": "pending"
    },
    {
      "finding_id": "F-002",
      "action": "Conduct risk profile reassessment",
      "owner": "Jane Doe",
      "deadline": "2025-01-08",
      "status": "pending"
    },
    {
      "action": "Implement FDS deadline monitoring",
      "owner": "Compliance team",
      "deadline": "2025-01-31",
      "status": "pending",
      "type": "process_improvement"
    }
  ],
  "report_url": "https://compliance.advisory.com/reports/AUD-2024-Q4-001",
  "generated": "2024-12-23T15:30:00Z",
  "reviewed_by": "Compliance Manager"
}
```

## Audit Areas

| Area | Checks | Weight |
|------|--------|--------|
| Best Interests Duty | 7 safe harbour steps | 30% |
| SOA Quality | Sections, accuracy, clarity | 25% |
| Documentation | Completeness, currency | 20% |
| Professional Standards | CPD, ethics | 15% |
| Regulatory Compliance | FSG, FDS, conflicts | 10% |

## Severity Levels

| Severity | Definition | Remediation |
|----------|------------|-------------|
| Critical | Regulatory breach, client harm risk | Immediate, escalate |
| High | Material non-compliance | Within 14 days |
| Medium | Process gap, improvement needed | Within 30 days |
| Low | Best practice enhancement | Within 60 days |

## Sampling Methodology

| Sample Type | Description |
|-------------|-------------|
| Random | Pure random selection |
| Stratified | Proportional by adviser/product |
| Targeted | Based on risk indicators |
| Census | All files in period |

## Notes

- Audit results reported to responsible manager
- Critical findings escalate to board/ASIC if required
- Remediation tracking until closure
- Trend analysis identifies systemic issues
- Annual audit required at minimum
