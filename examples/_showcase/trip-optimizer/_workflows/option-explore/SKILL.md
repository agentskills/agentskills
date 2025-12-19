---
name: option-explore
description: |
  Deep exploration of a single trip option. Recursively refines pricing
  and availability by trying date variations and alternative routes.
level: 3
operation: READ
composes:
  - option-explore        # Self-recursion for iterative refinement
  - route-price           # L2: Get flights + hotels pricing
  - destination-evaluate  # L2: Update quality score with new data
  - activity-search       # L1: Find things to do
license: Apache-2.0
---

# Option Explore

A Level 3 workflow that performs deep exploration of a single trip destination. Uses recursion to iteratively refine the option by trying date variations, alternative airports, and different hotel tiers.

## Why This is Level 3

This skill contains:
- **Self-recursion**: Explores variations of the same destination
- **Loop**: Iterates through date variations and alternatives
- **Dynamic dispatch**: Chooses which variations to explore based on results

## Composition Graph

```
option-explore (Level 3, READ)
├── option-explore        # Recurse on promising variations
├── route-price           # L2: Calculate total cost
├── destination-evaluate  # L2: Score the destination
└── activity-search       # L1: Find activities
```

## Algorithm

```
option-explore(destination, dates, constraints):
│
├── 1. GET BASELINE PRICING
│   ├── route-price(origin → destination, dates)
│   │   ├── flight-search → exact prices
│   │   └── hotel-search → exact prices
│   └── Calculate total_cost
│
├── 2. CHECK BUDGET FIT
│   ├── IF total_cost > budget × 1.1:
│   │   └── RETURN early with "over_budget" flag
│   └── ELSE: continue exploration
│
├── 3. ENRICH WITH ACTIVITIES
│   ├── activity-search(destination, preferences)
│   └── Update quality_score based on activity matches
│
├── 4. TRY VARIATIONS (recursive fan-out)
│   │
│   ├── Date shifts (if flexible):
│   │   ├── option-explore(destination, dates - 1 day)
│   │   └── option-explore(destination, dates + 1 day)
│   │
│   ├── Nearby airports:
│   │   ├── option-explore(destination, dates, alt_airport_1)
│   │   └── option-explore(destination, dates, alt_airport_2)
│   │
│   └── Hotel tier adjustments:
│       ├── option-explore(destination, dates, hotel_tier - 1)
│       └── option-explore(destination, dates, hotel_tier + 1)
│
├── 5. EARLY TERMINATION
│   ├── IF variation_improvement < exploration_cost:
│   │   └── STOP exploring further variations
│   └── ELSE: continue with most promising branch
│
└── 6. RETURN best variation found
    ├── total_cost (refined)
    ├── quality_score (updated)
    ├── booking_details (specific flights, hotels)
    └── variations_tried (for transparency)
```

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `destination` | string | Yes | - | Destination city or region |
| `dates` | object | Yes | - | Start and end dates |
| `origin` | string | Yes | - | Departure city/airport |
| `budget` | number | Yes | - | Maximum total cost |
| `preferences` | object | No | `{}` | Activity preferences |
| `max_variations` | number | No | `5` | Max variations to explore |
| `recursion_depth` | number | No | `2` | Max recursion depth |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `best_option` | object | Optimal configuration found |
| `total_cost` | number | Refined total cost |
| `quality_score` | number | Updated quality score |
| `flights` | object | Specific flight details |
| `hotels` | object | Specific hotel details |
| `activities` | list | Recommended activities |
| `variations_tried` | list | All variations explored |
| `savings_found` | number | Cost reduction from baseline |

## Example Execution

```
option-explore("Puerto Vallarta", March 15-22, origin="SFO", budget=2000):
│
├── Baseline: $1,340 (Alaska $380 + Hotel $120×7 + activities)
│
├── Variation 1: March 14-21 (shift -1 day)
│   └── $1,290 ✓ BETTER (-$50)
│
├── Variation 2: March 16-23 (shift +1 day)
│   └── $1,380 ✗ worse
│
├── Variation 3: Fly from OAK instead
│   └── $1,320 ✗ slightly worse
│
├── Variation 4: 3-star hotel instead of 4-star
│   └── $1,150 ✓ BETTER but quality_score drops
│
└── RETURN: March 14-21 configuration
    ├── total_cost: $1,290
    ├── quality_score: 0.84
    ├── savings_found: $50
    └── variations_tried: 4
```

## Recursion Bounds

To prevent infinite exploration:
- `max_variations`: Limits breadth of exploration
- `recursion_depth`: Limits depth of nested variations
- Early termination when improvements become marginal

## Notes

- This workflow is called by `trip-optimize` as part of Phase 4
- Self-recursion enables finding local optima efficiently
- The quality vs cost trade-off is surfaced to the parent workflow
- All prices are fetched in real-time, not cached
