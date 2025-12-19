---
name: route-price
description: |
  Calculate precise total cost for a trip route including flights,
  hotels, and estimated daily expenses.
level: 2
operation: READ
composes:
  - flight-search
  - hotel-search
license: Apache-2.0
---

# Route Price

A Level 2 composite that calculates the total cost for a specific trip configuration.

## Composition Graph

```
route-price (Level 2, READ)
├── flight-search    # L1: Get exact flight prices
└── hotel-search     # L1: Get exact hotel prices
```

## Calculation

```
total_cost = (
    flight_cost +           # Round-trip airfare
    hotel_cost × nights +   # Accommodation
    daily_expenses × days   # Food, transport, activities estimate
)
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Departure airport code |
| `destination` | string | Yes | Arrival city |
| `dates` | object | Yes | Check-in and check-out dates |
| `hotel_tier` | string | No | budget / mid / luxury |
| `travelers` | number | No | Number of travelers |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `total_cost` | number | Complete trip cost |
| `flights` | object | Flight details and price |
| `hotels` | object | Hotel details and price |
| `breakdown` | object | Cost breakdown by category |

## Example

```
route-price("SFO", "Puerto Vallarta", March 14-21, hotel_tier="mid"):

├── flight-search → Alaska AS1234, $380 RT
└── hotel-search → Marriott, $120/night × 7 = $840

RETURN:
  total_cost: $1,570
  breakdown:
    flights: $380
    hotels: $840
    daily_expenses: $350 (estimated)
```
