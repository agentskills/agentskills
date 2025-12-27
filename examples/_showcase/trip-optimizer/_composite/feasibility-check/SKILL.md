---
name: feasibility-check
description: |
  Binary constraint check for trip feasibility. Returns pass/fail
  on hard constraints: visa, budget, dates, flight duration.
level: 2
operation: READ
composes:
  - visa-check
  - calendar-read
  - route-price
license: Apache-2.0
---

# Feasibility Check

A Level 2 composite that performs binary constraint validation. Used to filter out impossible options before expensive deep research.

## Why Binary Constraints Matter

Checking hard constraints first prevents wasted compute:
- No point researching a destination if visa takes 3 months
- No point pricing flights if dates don't match availability
- No point exploring if clearly over budget

## Composition Graph

```
feasibility-check (Level 2, READ)
├── visa-check      # L1: Visa requirements
├── calendar-read   # L1: User's available dates
└── route-price     # L2: Quick cost estimate
```

## Constraint Logic

```
is_feasible = (
    NOT visa_required OR visa_processing_time < days_until_trip
    AND estimated_cost <= budget × 1.2  # 20% buffer for estimates
    AND dates ∈ user_available_dates
    AND flight_duration <= max_flight_hours
)
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination` | string | Yes | Destination to check |
| `dates` | object | Yes | Proposed travel dates |
| `budget` | number | Yes | Maximum budget |
| `max_flight_hours` | number | No | Flight duration limit |
| `passport_country` | string | No | For visa checking |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `is_feasible` | boolean | Pass/fail result |
| `failed_constraints` | list | Which constraints failed |
| `constraint_details` | object | Details on each check |

## Example

```
feasibility-check("Bali", March 15-22, budget=2000, max_flight=8):

├── visa-check → Visa on arrival OK
├── calendar-read → March 15-22 available ✓
├── route-price → ~$1,800 estimate ✓
└── flight_duration → 18 hours ✗

RETURN:
  is_feasible: false
  failed_constraints: ["flight_duration"]
  constraint_details:
    visa: "pass"
    budget: "pass"
    dates: "pass"
    flight: "fail - 18hr > 8hr max"
```
