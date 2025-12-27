---
name: calendar-read
description: Read user's calendar to find available date ranges for travel.
level: 1
operation: READ
license: Apache-2.0
---

# Calendar Read

A Level 1 atomic skill that checks user's calendar availability.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes | Start of search range |
| `end_date` | string | Yes | End of search range |
| `min_days` | number | No | Minimum consecutive free days needed |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `available_ranges` | list | Date ranges with no conflicts |
| `blocked_dates` | list | Dates with existing commitments |

## Example

```
calendar-read("2024-03-01", "2024-04-30", min_days=7):

RETURN:
  available_ranges:
    - start: "2024-03-15"
      end: "2024-03-22"
      days: 7
    - start: "2024-04-05"
      end: "2024-04-12"
      days: 7
  blocked_dates:
    - "2024-03-10" # meeting
    - "2024-04-01" # deadline
```
