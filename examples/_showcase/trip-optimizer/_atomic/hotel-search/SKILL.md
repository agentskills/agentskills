---
name: hotel-search
description: Search for hotels at a destination for specific dates. Returns prices, ratings, and amenities.
level: 1
operation: READ
license: Apache-2.0
---

# Hotel Search

A Level 1 atomic skill that searches for hotels via travel APIs.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination` | string | Yes | City or area |
| `check_in` | string | Yes | Check-in date (YYYY-MM-DD) |
| `check_out` | string | Yes | Check-out date (YYYY-MM-DD) |
| `guests` | number | No | Number of guests |
| `tier` | string | No | budget / mid / luxury |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `hotels` | list | Available hotel options |
| `lowest_price` | number | Cheapest per-night rate |
| `best_rated` | object | Highest rated option |

## Example

```
hotel-search("Puerto Vallarta", "2024-03-15", "2024-03-22", tier="mid"):

RETURN:
  hotels:
    - name: "Marriott Puerto Vallarta"
      price_per_night: $120
      rating: 4.2
      amenities: ["pool", "beach", "spa"]
    - name: "Hyatt Ziva"
      price_per_night: $180
      rating: 4.5
      amenities: ["all-inclusive", "pool", "beach"]
  lowest_price: $120
  best_rated: "Hyatt Ziva"
```
