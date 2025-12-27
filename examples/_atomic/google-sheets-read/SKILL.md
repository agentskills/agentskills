---
name: google-sheets-read
description: Read data from a Google Sheets spreadsheet. Fetch specific ranges, entire sheets, or search for values. Use for data analysis, reporting, or syncing.
level: 1
operation: READ
license: Apache-2.0
---

# Google Sheets Read

Read data from a Google Sheets spreadsheet.

## When to Use

Use this skill when:
- Fetching data for analysis or reporting
- Reading configuration stored in spreadsheets
- Syncing data from sheets to other systems
- Looking up values in a sheet

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spreadsheet_id` | string | Yes | The spreadsheet ID (from URL) |
| `range` | string | No | A1 notation range (e.g., "Sheet1!A1:D10") |
| `sheet_name` | string | No | Sheet name (if not using range) |
| `value_render_option` | string | No | How values are rendered: FORMATTED_VALUE, UNFORMATTED_VALUE, FORMULA |
| `major_dimension` | string | No | Return by ROWS or COLUMNS (default: ROWS) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `values` | any[][] | 2D array of cell values |
| `range` | string | The actual range that was read |
| `major_dimension` | string | How data is organised |

## Usage

```
Read Google Sheet 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms range "Sheet1!A1:D10"
```

```
Fetch all data from the "Inventory" sheet in spreadsheet abc123xyz
```

## Example Response

```json
{
  "values": [
    ["Name", "Email", "Role", "Start Date"],
    ["Alice", "alice@example.com", "Engineer", "2024-01-15"],
    ["Bob", "bob@example.com", "Designer", "2024-02-01"]
  ],
  "range": "Sheet1!A1:D3",
  "major_dimension": "ROWS"
}
```

## Why This Matters for Composition

As a READ operation, `google-sheets-read` provides data for workflows:
- **expense-report** (Level 2) can read expenses + generate summary
- **team-roster** (Level 3) can sync sheet data to other systems

## Notes

- Requires Google Sheets API authentication
- Spreadsheet ID is the long string in the sheet URL
- Empty cells are represented as empty strings
- For large sheets, use specific ranges to limit data
- Inspired by n8n's Google Sheets node (Read operation)
