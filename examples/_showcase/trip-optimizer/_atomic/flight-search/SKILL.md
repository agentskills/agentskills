---
name: flight-search
description: Search for flights between two airports on specific dates. Returns prices, times, and airlines.
level: 1
operation: READ
license: Apache-2.0
---

# Flight Search

A Level 1 atomic skill that searches for flights via travel APIs.

## Why This is Level 1

- Single operation: Query flight API
- No composition (wraps primitive directly)
- Stateless, no decision logic

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Departure airport code (e.g., "SFO") |
| `destination` | string | Yes | Arrival airport code (e.g., "PVR") |
| `departure_date` | string | Yes | Outbound date (YYYY-MM-DD) |
| `return_date` | string | No | Return date for round-trip |
| `travelers` | number | No | Number of passengers |
| `cabin_class` | string | No | economy / business / first |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `flights` | list | Available flight options |
| `lowest_price` | number | Cheapest option found |
| `fastest_duration` | number | Shortest flight time |

## Example

```
flight-search("SFO", "PVR", "2024-03-15", return="2024-03-22"):

RETURN:
  flights:
    - airline: "Alaska"
      price: $380
      duration: "3h 15m"
      stops: 0
    - airline: "United"
      price: $420
      duration: "3h 10m"
      stops: 0
    - airline: "American"
      price: $350
      duration: "5h 30m"
      stops: 1
  lowest_price: $350
  fastest_duration: "3h 10m"
```
