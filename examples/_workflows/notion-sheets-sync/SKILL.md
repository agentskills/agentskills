---
name: notion-sheets-sync
description: Bidirectional sync between a Notion database and Google Sheets. Detects changes in either system and propagates updates while handling conflicts.
level: 3
operation: WRITE
license: Apache-2.0
composes:
  - notion-database-query
  - google-sheets-read
  - google-sheets-append
  - notion-page-update
  - data-merge
---

# Notion Sheets Sync

Keep a Notion database and Google Sheet in sync with bidirectional updates.

## When to Use

Use this skill when:
- Team uses Notion for planning but stakeholders need spreadsheet access
- Financial data needs to flow between Notion and Sheets
- Creating a "single source of truth" across platforms
- Building dashboards from Notion data in Sheets

## Workflow Steps

```
1. READ: Fetch current state from both systems
       │
       ├── Notion database query
       └── Google Sheets read
               │
               ▼
2. COMPARE: Identify changes since last sync
       │
       ├── New in Notion → Add to Sheets
       ├── New in Sheets → Add to Notion
       ├── Modified in Notion → Update Sheets
       ├── Modified in Sheets → Update Notion
       └── Conflicts → Apply resolution strategy
               │
               ▼
3. MERGE: Combine changes using data-merge
       │
       ▼
4. WRITE: Apply updates to both systems
       │
       ├── google-sheets-append/update
       └── notion-page-update
               │
               ▼
5. RECORD: Update sync checkpoint
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `notion_database_id` | string | Yes | Notion database ID |
| `spreadsheet_id` | string | Yes | Google Sheets spreadsheet ID |
| `sheet_name` | string | No | Sheet tab name (default: first sheet) |
| `sync_key` | string | Yes | Field to use as unique identifier |
| `field_mapping` | object | Yes | Map Notion properties to Sheet columns |
| `conflict_strategy` | string | No | newest_wins, notion_wins, sheets_wins (default: newest_wins) |
| `sync_direction` | string | No | bidirectional, notion_to_sheets, sheets_to_notion |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `synced_at` | string | Sync completion timestamp |
| `notion_to_sheets` | object | Records pushed to Sheets |
| `sheets_to_notion` | object | Records pushed to Notion |
| `conflicts_resolved` | object[] | Conflicts and how they were resolved |
| `errors` | object[] | Any sync failures |

## Usage

```
Sync Notion database "abc123" with Google Sheet "1xyz789", using "email" as the key field. Map Notion "Name" to column A, "Status" to column B, "Due Date" to column C.
```

```
One-way sync from Notion project tracker to stakeholder spreadsheet, updating every hour
```

## Example Response

```json
{
  "synced_at": "2024-12-23T14:30:00Z",
  "notion_to_sheets": {
    "added": 3,
    "updated": 7,
    "unchanged": 45
  },
  "sheets_to_notion": {
    "added": 1,
    "updated": 2,
    "unchanged": 52
  },
  "conflicts_resolved": [
    {
      "key": "alice@example.com",
      "field": "Status",
      "notion_value": "In Progress",
      "sheets_value": "Done",
      "resolved_to": "Done",
      "reason": "Sheets was newer (2024-12-23T14:00:00Z vs 2024-12-22T10:00:00Z)"
    }
  ],
  "errors": []
}
```

## Why Level 3

This workflow demonstrates:
1. **Complex orchestration**: Multiple reads, comparison logic, multiple writes
2. **State management**: Tracks sync checkpoints across runs
3. **Conflict resolution**: Decision logic for competing updates
4. **Bidirectional flow**: Not just read→write but continuous sync
5. **Composes Level 2**: Uses `data-merge` for intelligent combination

## Composition Graph

```
notion-sheets-sync (Level 3)
    │
    ├── notion-database-query (L1)
    │           │
    ├───────────┼── google-sheets-read (L1)
    │           │           │
    │           ▼           ▼
    │       ┌───────────────────┐
    │       │    data-merge     │ (L2)
    │       │  [Compare/Diff]   │
    │       └─────────┬─────────┘
    │                 │
    │    ┌────────────┼────────────┐
    │    ▼            ▼            ▼
    │ [Notion→]   [Conflicts]   [→Sheets]
    │    │            │            │
    │    ▼            ▼            ▼
    ├── notion-page-update      google-sheets-append
    │        (L1)                    (L1)
    │
    └── [Record checkpoint]
```

## Notes

- First sync may take longer (full comparison)
- Subsequent syncs use change detection for efficiency
- Consider Notion API rate limits (3 requests/second)
- Inspired by n8n template "Sync Notion database to Google Sheets"
- For one-way sync, set `sync_direction` appropriately
