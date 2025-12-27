---
name: data-merge
description: Merge data from multiple sources into a unified dataset. Supports inner/outer/left/right joins on specified keys. Use when combining data from different APIs or files.
level: 2
operation: READ
license: Apache-2.0
composes:
  - http-request
  - google-sheets-read
---

# Data Merge

Combine data from multiple sources into a single unified dataset.

## When to Use

Use this skill when:
- Combining data from different APIs (e.g., CRM + billing system)
- Merging spreadsheet data with database records
- Creating unified views across multiple data sources
- Enriching records with data from another source

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sources` | object[] | Yes | Array of data sources to merge |
| `join_type` | string | No | Join type: inner, outer, left, right (default: left) |
| `join_key` | string | Yes | Field name to join on |
| `output_fields` | string[] | No | Fields to include in output (default: all) |

Each source object:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Identifier for this source |
| `type` | string | Source type: api, sheets, json |
| `config` | object | Source-specific configuration |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `merged_data` | object[] | Array of merged records |
| `match_count` | integer | Records that matched across sources |
| `unmatched` | object | Count of unmatched records per source |

## Usage

```
Merge customer data from our CRM API (https://api.crm.com/customers) with billing data from Google Sheet "1abc123" using "email" as the join key
```

```
Combine GitHub issues from repos anthropics/claude-code and anthropics/sdk using issue title as join key to find duplicates
```

## Example Response

```json
{
  "merged_data": [
    {
      "email": "alice@example.com",
      "crm_name": "Alice Smith",
      "crm_status": "active",
      "billing_plan": "enterprise",
      "billing_mrr": 5000
    }
  ],
  "match_count": 150,
  "unmatched": {
    "crm": 12,
    "billing": 3
  }
}
```

## Why Level 2

This skill composes multiple Level 1 skills:
- Uses `http-request` to fetch API data
- Uses `google-sheets-read` for spreadsheet sources
- Adds join logic that doesn't exist in either atomic skill

The value is in the **combination**: fetching from multiple sources and intelligently merging them.

## Notes

- Large datasets may be paginated
- Join keys must exist in all sources being joined
- For complex transformations, consider `data-transform` skill
- Inspired by n8n's Merge node
