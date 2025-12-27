---
name: document-generate
description: Generate compliant financial documents from templates. Supports FSG, SOA, risk profiles, fee disclosures, and review agendas. Populates with client data and applies regulatory formatting.
level: 1
operation: WRITE
license: Apache-2.0
domain: financial-advisory
tool_discovery:
  document_engine:
    prefer: [xplan-docgen, templafy-generate, docusign-generate]
    fallback: pandoc-generate
---

# Document Generate

Generate regulatory-compliant financial advisory documents.

## When to Use

Use this skill when:
- Preparing documents for client meetings
- Creating Statement of Advice (SOA)
- Generating Financial Services Guide (FSG)
- Producing risk profile assessments
- Creating fee disclosure statements

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template` | string | Yes | Template type: fsg, soa, risk_profile, fee_disclosure, review_agenda, record_of_advice |
| `client_id` | string | Yes | Client identifier for data population |
| `data` | object | No | Additional data to merge into template |
| `format` | string | No | Output format: pdf, docx, html (default: pdf) |
| `version` | string | No | Template version (default: latest) |
| `draft` | boolean | No | Mark as draft with watermark (default: false) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | string | Unique document identifier |
| `url` | string | URL to access document |
| `format` | string | Generated format |
| `pages` | integer | Page count |
| `template_version` | string | Template version used |
| `compliance_checks` | object | Regulatory requirement verification |
| `archived` | boolean | Whether archived for retention |

## Supported Templates

### Financial Services Guide (FSG)
Required disclosures about adviser and services:
- Adviser credentials and authorisations
- Services offered and limitations
- Fee structure and payment methods
- Complaint handling procedures
- Relationships and associations

### Statement of Advice (SOA)
Formal advice document with required sections:
- Advice scope and limitations
- Client situation summary
- Recommendations with rationale
- Risk warnings and disclosures
- Best interests duty statement
- Fee and conflict disclosure
- Product information
- Alternatives considered

### Risk Profile Assessment
- Risk tolerance questionnaire results
- Risk capacity analysis
- Recommended risk classification
- Asset allocation guidance
- Client acknowledgment section

### Fee Disclosure Statement (FDS)
- Ongoing fee arrangements
- Services provided for fees
- Fee calculation methodology
- Opt-in consent section

### Review Agenda
- Meeting objectives
- Discussion topics checklist
- Pre-populated client data
- Action item template

## Usage

```
Generate SOA for client C-12345 recommending super consolidation
```

```
Create FSG for new client discovery meeting
```

```
Prepare fee disclosure statement for annual renewal
```

## Example Response

```json
{
  "document_id": "DOC-2024-12-23-SOA-001234",
  "url": "https://docs.advisory.com/view/DOC-2024-12-23-SOA-001234",
  "format": "pdf",
  "pages": 24,
  "template_version": "3.2.1",
  "compliance_checks": {
    "client_details_complete": true,
    "risk_profile_current": true,
    "best_interests_statement": true,
    "fee_disclosure": true,
    "conflicts_disclosed": true,
    "product_details": true,
    "alternatives_considered": true,
    "signature_blocks": true
  },
  "warnings": [],
  "archived": true,
  "retention_until": "2031-12-23"
}
```

## Template Sections (SOA)

| Section | Required | Description |
|---------|----------|-------------|
| Cover page | Yes | Client name, date, adviser details |
| Scope of advice | Yes | What is/isn't covered |
| Your situation | Yes | Objectives, needs, circumstances |
| Risk profile | Yes | Tolerance, capacity, appropriate category |
| Recommendations | Yes | Specific advice with rationale |
| Why this is appropriate | Yes | Best interests duty compliance |
| Risks | Yes | Significant risks of recommendations |
| Fees and costs | Yes | All applicable fees disclosed |
| Conflicts | Yes | Any conflicts of interest |
| Products | Conditional | If product recommendations made |
| Alternatives | Conditional | If products compared |
| Next steps | Yes | Implementation actions |
| Authority to proceed | Yes | Client signature block |

## Compliance Verification

Before generation, the system verifies:
1. Client risk profile is current (within 12 months)
2. All required sections have content
3. Fee disclosures match fee schedule
4. Best interests duty statement included
5. Product warnings present for each recommendation
6. Adviser authorisation covers advice type

## Notes

- Documents automatically archived per retention policy (7 years)
- Draft watermark prevents client distribution
- Version control tracks all document iterations
- Signature blocks integrate with DocuSign/Adobe Sign
- Template updates require compliance approval
