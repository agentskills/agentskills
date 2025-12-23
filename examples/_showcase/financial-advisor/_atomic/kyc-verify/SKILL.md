---
name: kyc-verify
description: Perform Know Your Client (KYC) and Anti-Money Laundering (AML) verification. Checks identity documents, screens against sanctions lists, and assesses risk.
level: 1
operation: READ
license: Apache-2.0
domain: financial-advisory
tool_discovery:
  verification:
    prefer: [greenid-verify, illion-verify, equifax-verify]
    fallback: manual-verify
---

# KYC Verify

Perform identity verification and AML/CTF compliance checks.

## When to Use

Use this skill when:
- Onboarding new clients
- Re-verifying existing clients (every 2 years)
- Client details change (name, address)
- Suspicious activity flagged
- High-value transaction threshold exceeded

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `verification_type` | string | Yes | Type: full, refresh, enhanced, transaction |
| `documents` | object[] | No | Uploaded identity documents |
| `transaction_context` | object | No | Context for transaction-based checks |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `verified` | boolean | Overall verification status |
| `verification_level` | string | Level achieved: basic, standard, enhanced |
| `checks_performed` | object[] | Individual check results |
| `risk_rating` | string | AML risk: low, medium, high |
| `pep_status` | boolean | Politically Exposed Person flag |
| `sanctions_clear` | boolean | Sanctions screening result |
| `valid_until` | string | Verification expiry date |
| `required_actions` | object[] | Any follow-up needed |

## Verification Levels

| Level | Requirements | Use Case |
|-------|--------------|----------|
| `basic` | Name + DOB + address match | Low-risk, small accounts |
| `standard` | + ID document verified | Standard clients |
| `enhanced` | + Source of funds, PEP check | High-value, high-risk |

## Checks Performed

| Check | Description | Source |
|-------|-------------|--------|
| Identity match | Name, DOB, address | Government databases |
| Document authenticity | ID document verification | Document AI + databases |
| Address verification | Current address confirmation | Electoral roll, utilities |
| PEP screening | Politically exposed persons | Global PEP databases |
| Sanctions screening | Global sanctions lists | OFAC, EU, UN, DFAT |
| Adverse media | Negative news screening | Media databases |

## Usage

```
Run full KYC verification for new client John Smith
```

```
Refresh verification for client C-12345 (2-year renewal)
```

```
Enhanced due diligence for high-value transaction
```

## Example Response

```json
{
  "verified": true,
  "verification_level": "standard",
  "client_id": "C-12345",
  "checks_performed": [
    {
      "check": "identity_match",
      "status": "pass",
      "confidence": 98,
      "source": "DVS (Document Verification Service)"
    },
    {
      "check": "document_authenticity",
      "status": "pass",
      "document_type": "passport",
      "document_number": "PA1234567",
      "expiry": "2029-06-15"
    },
    {
      "check": "address_verification",
      "status": "pass",
      "source": "electoral_roll",
      "address_confirmed": "123 Collins St, Melbourne VIC 3000"
    },
    {
      "check": "pep_screening",
      "status": "clear",
      "source": "Dow Jones, Refinitiv"
    },
    {
      "check": "sanctions_screening",
      "status": "clear",
      "lists_checked": ["OFAC", "EU", "UN", "DFAT"]
    },
    {
      "check": "adverse_media",
      "status": "clear",
      "source": "LexisNexis"
    }
  ],
  "risk_rating": "low",
  "pep_status": false,
  "sanctions_clear": true,
  "valid_until": "2026-12-23",
  "audit_reference": "KYC-2024-12-23-001234"
}
```

## Risk Rating Factors

| Factor | Low Risk | Medium Risk | High Risk |
|--------|----------|-------------|-----------|
| Country | Australia, NZ, UK | EU, US, Japan | FATF high-risk |
| Occupation | Employed, retired | Self-employed, cash business | PEP, high-profile |
| Source of funds | Salary, pension | Business income | Inheritance, overseas |
| Transaction patterns | Regular, predictable | Variable | Large, irregular |
| Account type | Personal | SMSF, trust | Complex structures |

## Required Actions by Outcome

| Outcome | Required Action |
|---------|-----------------|
| Verification passed | Proceed with onboarding |
| Document issues | Request replacement documents |
| Address mismatch | Request proof of address |
| PEP identified | Enhanced due diligence |
| Sanctions match | Immediate escalation to MLRO |
| Adverse media | Risk assessment required |

## Compliance Notes

- All verification results stored for 7 years
- Audit trail of all checks performed
- Suspicious matters must be reported within 24 hours
- Re-verification required every 2 years
- Enhanced checks for transactions >$10,000 AUD
