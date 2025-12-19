---
name: destination-evaluate
description: |
  Evaluate a destination for trip suitability. Combines weather data,
  activity availability, visa requirements, and estimated costs into
  a composite quality score.
level: 2
operation: READ
composes:
  - weather-fetch
  - activity-search
  - visa-check
  - flight-search
license: Apache-2.0
---

# Destination Evaluate

A Level 2 composite that scores a destination across multiple dimensions. Used in the fan-out phase of trip optimization to quickly assess many candidates in parallel.

## Why This is Level 2

- Composes multiple Level 1 atomics
- No loops or recursion
- Simple aggregation logic (weighted scoring)
- Stateless

## Composition Graph

```
destination-evaluate (Level 2, READ)
├── weather-fetch      # L1: Historical weather data
├── activity-search    # L1: Available activities
├── visa-check         # L1: Visa requirements
└── flight-search      # L1: Estimated flight cost/duration
```

## Scoring Algorithm

```
quality_score = (
    weather_score × 0.30 +      # 30% weight
    activity_score × 0.25 +     # 25% weight
    value_score × 0.25 +        # 25% weight
    convenience_score × 0.20    # 20% weight
)

WHERE:
  weather_score = P(sunshine) × (1 - P(rain))
  activity_score = matched_activities / desired_activities
  value_score = quality_indicators / estimated_cost
  convenience_score = 1 / (1 + flight_hours + visa_complexity)
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination` | string | Yes | City or region to evaluate |
| `dates` | object | Yes | Travel date range |
| `origin` | string | Yes | Departure city (for flight estimates) |
| `preferences` | object | No | Activity type preferences |
| `passport_country` | string | No | For visa checking |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `quality_score` | number | Composite score 0-1 |
| `weather` | object | Temperature, sunshine probability, rain risk |
| `activities` | list | Matching activities found |
| `visa_required` | boolean | Whether visa is needed |
| `estimated_cost` | number | Rough trip cost estimate |
| `flight_duration` | number | Estimated flight hours |
| `breakdown` | object | Individual dimension scores |

## Example

```
destination-evaluate("Cabo San Lucas", dates=March 15-22, origin="SFO"):

├── weather-fetch → 92% sunshine, 75°F avg, 5% rain
├── activity-search → beaches, snorkeling, fishing, nightlife
├── visa-check → No visa required for US passport
└── flight-search → ~3hr, ~$400 estimate

RETURN:
  quality_score: 0.82
  breakdown:
    weather: 0.91
    activities: 0.85
    value: 0.75
    convenience: 0.78
```

## Notes

- This is a fast evaluation for initial screening
- Detailed pricing comes later via `route-price`
- Parallelizable - run on many destinations simultaneously
