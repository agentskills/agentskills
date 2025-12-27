---
name: compliance-check
description: Verify regulatory compliance for specific actions, documents, or client situations. Returns pass/fail with detailed findings and remediation steps.
level: 1
operation: READ
license: Apache-2.0
domain: financial-advisory
---

# Compliance Check

Verify regulatory compliance requirements.

## When to Use

Use this skill when:
- Before providing advice (best interests duty)
- Before executing trades (appropriateness)
- During document preparation (completeness)
- Periodic compliance audits
- Adviser professional development tracking

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `check_type` | string | Yes | Type: best_interests, kyc, aml, pd_hours, document, suitability, conflicts |
| `subject_id` | string | Yes | Client, adviser, or document ID |
| `context` | object | No | Additional context for the check |
| `as_of_date` | string | No | Check compliance as of date (default: now) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `passed` | boolean | Overall compliance status |
| `check_type` | string | Type of check performed |
| `findings` | object[] | Detailed findings |
| `score` | integer | Compliance score (0-100) |
| `remediation` | object[] | Required actions if failed |
| `expires` | string | When check result expires |
| `audit_reference` | string | Audit log reference |

## Check Types

### Best Interests Duty (s961B)
Verifies advice meets statutory requirements:
- Client objectives identified
- Needs analysis complete
- Circumstances considered
- Reasonable investigations made
- Alternatives assessed
- Strategy in client's best interests

### Know Your Client (KYC)
Identity and verification status:
- Identity documents verified
- Source of funds confirmed
- Politically exposed person check
- Sanctions screening
- Verification currency (within 2 years)

### Anti-Money Laundering (AML/CTF)
Transaction monitoring compliance:
- Customer due diligence complete
- Suspicious matter reporting
- Transaction monitoring active
- Record keeping compliant

### Professional Development (PD)
Adviser CPD compliance:
- Hours completed (40 annual requirement)
- Tax component (minimum 5 hours)
- Ethics component
- Specialisation requirements

### Document Compliance
Document completeness and accuracy:
- Required sections present
- Disclosures complete
- Signatures obtained
- Version control maintained

### Suitability
Product/strategy appropriateness:
- Risk profile match
- Investment horizon appropriate
- Concentration limits
- Client understanding confirmed

## Usage

```
Check best interests duty compliance for SOA-2024-001234
```

```
Verify KYC status for client C-12345
```

```
Check professional development hours for adviser Jane Doe
```

## Example Response

```json
{
  "passed": false,
  "check_type": "best_interests",
  "score": 75,
  "findings": [
    {
      "requirement": "reasonable_investigations",
      "status": "pass",
      "detail": "Product research documented"
    },
    {
      "requirement": "alternatives_considered",
      "status": "fail",
      "detail": "Only one product option documented, minimum 3 required",
      "severity": "high"
    },
    {
      "requirement": "client_objectives",
      "status": "pass",
      "detail": "Retirement income goal clearly documented"
    }
  ],
  "remediation": [
    {
      "action": "document_alternatives",
      "description": "Add comparison of at least 2 additional product options",
      "deadline": "before_advice_delivery",
      "assigned_to": "adviser"
    }
  ],
  "expires": "2024-12-24T00:00:00Z",
  "audit_reference": "CHK-2024-12-23-001234"
}
```

## Best Interests Checklist

| Requirement | Verification |
|-------------|--------------|
| Identify objectives | Goals documented in client file |
| Identify needs | Needs analysis completed |
| Identify circumstances | Fact-find current (12 months) |
| Reasonable investigations | Product research on file |
| Assess strategies | Multiple strategies considered |
| Prioritise interests | No conflicting personal interests |
| Appropriate advice | Matches risk profile and objectives |

## Severity Levels

| Severity | Impact | Action Required |
|----------|--------|-----------------|
| `critical` | Cannot proceed | Immediate remediation |
| `high` | Material breach | Remediate before proceeding |
| `medium` | Improvement needed | Remediate within 7 days |
| `low` | Best practice | Remediate when convenient |

## Notes

- All checks create audit log entries
- Failed checks can block workflow progression
- Check results cached for 24 hours (configurable)
- Remediation tracking until resolution
- Escalation to compliance officer for critical findings
