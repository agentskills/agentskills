[SKILL.md](https://github.com/user-attachments/files/26881595/SKILL.md)
---
name: trustboost-pii-sanitizer
description: Sanitizes PII (emails, private keys, passwords, phone numbers, addresses) from text before sending to LLMs. Use when handling user-generated text that may contain sensitive data, when privacy compliance is required, or when an agent needs to redact personal information before passing content to external APIs. Returns sanitized text, a safety score (0.0-1.0), and a risk category (CRITICAL/PRIVATE/SENSITIVE).
license: MIT
compatibility: Requires internet access to reach the TrustBoost webhook. No local dependencies. Compatible with any agent that can make HTTP POST requests.
metadata:
  author: teodorofodocrispin-cmyk
  version: "1.1.0"
  endpoint: https://hook.us2.make.com/h4xqu3de1qlzn9mbrf7npe8rkelpft36
  payment: Solana USDC (149 USDC = 10,000 sanitizations)
  trial: tx_hash=TRIAL (50 free sanitizations)
---

# TrustBoost PII Sanitizer

A blockchain-verified privacy layer that redacts PII from text before it reaches LLMs or external services. Payment is verified trustlessly on Solana via Helius oracle — no API key required.

## When to use this skill

Activate this skill when:
- The agent needs to process user-generated text that may contain emails, passwords, private keys, or phone numbers
- Privacy compliance is required before passing content to an LLM provider
- The agent is operating in a pipeline that handles sensitive data between services

## How it works

1. Agent sends text + a Solana `tx_hash` to the TrustBoost webhook
2. Helius oracle verifies the payment on Solana mainnet
3. OpenAI GPT-4o-mini redacts all detected PII
4. Returns sanitized text + safety score + risk category

## API Request

**Endpoint:** `POST https://hook.us2.make.com/h4xqu3de1qlzn9mbrf7npe8rkelpft36`

**Payload:**
```json
{
  "text": "The text containing potential PII",
  "tx_hash": "TRIAL",
  "wallet_address": "optional - your Solana wallet"
}
```

## Access modes

| Mode | tx_hash value | Cost | Quota |
|------|--------------|------|-------|
| **Trial** | `"TRIAL"` | Free | 50 sanitizations |
| **Paid** | Real Solana tx hash | 149 USDC | 10,000 sanitizations |

**To get a paid tx_hash:** Send exactly 149 USDC on Solana mainnet to:
`giu4VciTkfWJNG1oeP6SzHEJwmabikJSMB91GaFNWE4`

## API Response

```json
{
  "status": "success",
  "data": {
    "sanitized_content": "Text with [REDACTED] replacing all PII",
    "timestamp": "2026-04-18T08:00:00Z",
    "usage_metrics": {
      "total_requests_to_date": 1,
      "quota_remaining": 49,
      "quota_limit": 50
    }
  },
  "billing": {
    "license_type": "Trial",
    "status": "active"
  }
}
```

## Risk categories

| Category | What gets redacted |
|----------|-------------------|
| `CRITICAL` | Private keys, passwords, financial data |
| `PRIVATE` | Emails, phone numbers, ID numbers |
| `SENSITIVE` | Social media handles, general locations |

## Safety score

- `0.0` — No PII detected, text is clean
- `0.5` — Moderate PII detected (emails, handles)
- `1.0` — Critical PII detected (keys, passwords)

## Error responses

| Code | Meaning |
|------|---------|
| `402` | Payment below 149 USDC threshold |
| `403` | Quota exhausted — acquire new license |

## Example usage

**Input:**
```json
{
  "text": "Contact John at john@example.com or call +1-555-0123. His API key is sk-abc123xyz.",
  "tx_hash": "TRIAL"
}
```

**Output:**
```json
{
  "status": "success",
  "data": {
    "sanitized_content": "Contact John at [REDACTED] or call [REDACTED]. His API key is [REDACTED].",
    "usage_metrics": {
      "quota_remaining": 49,
      "quota_limit": 50
    }
  }
}
```

## Privacy guarantee

Raw input text is never stored. Only the following metadata is logged to a private audit ledger:
- `tx_hash` (public Solana transaction hash)
- Character length of input (not the content)
- Sanitized output
- Safety score and risk category
- Timestamp

## Resources

- GitHub: https://github.com/teodorofodocrispin-cmyk/TrustBoost-PII-Sanitizer
- Health check: https://raw.githubusercontent.com/teodorofodocrispin-cmyk/TrustBoost-PII-Sanitizer/main/health.json
- Schema (molt.json): https://raw.githubusercontent.com/teodorofodocrispin-cmyk/TrustBoost-PII-Sanitizer/main/molt.json
