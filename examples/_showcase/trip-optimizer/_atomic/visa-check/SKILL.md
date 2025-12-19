---
name: visa-check
description: Check visa requirements for a destination based on passport country.
level: 1
operation: READ
license: Apache-2.0
---

# Visa Check

A Level 1 atomic skill that checks visa requirements.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination_country` | string | Yes | Country to visit |
| `passport_country` | string | Yes | Traveler's passport country |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `visa_required` | boolean | Whether visa is needed |
| `visa_type` | string | Type of visa if required |
| `processing_days` | number | Typical processing time |

## Example

```
visa-check("Mexico", passport_country="US"):

RETURN:
  visa_required: false
  visa_type: null
  processing_days: 0
```
