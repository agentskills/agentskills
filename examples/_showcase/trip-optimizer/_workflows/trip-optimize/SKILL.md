---
name: trip-optimize
description: |
  Multi-dimensional trip optimizer using expected value prioritization,
  gradient descent refinement, and early termination based on marginal returns.
  Finds optimal travel arrangements within budget and date constraints.
level: 3
operation: READ
composes:
  - trip-optimize           # Self-recursion for iterative refinement
  - option-explore          # L3: Deep exploration of promising options
  - destination-evaluate    # L2: Score destinations
  - feasibility-check       # L2: Binary constraint filtering
  - route-price             # L2: Calculate total trip cost
license: Apache-2.0
---

# Trip Optimize

A comprehensive trip planning workflow that demonstrates advanced composable skills patterns including fan-out parallelization, expected value optimization, gradient descent refinement, and game-theoretic compute efficiency.

## Problem Space

```
Example User Input:
├── Budget: $2,000
├── Dates available: March 15-22 OR April 5-12
├── Departure: San Francisco (SFO)
├── Preferences: Beach OR ski, good food, < 8hr flight OR 5hr drive
└── Constraints: No visa required (US passport)

Optimization Objectives:
├── Maximize: Experience quality, weather probability, value-for-money
├── Minimize: Travel time, hassle, risk
└── Constraint: Stay within budget, available dates only
```

## Algorithm Overview

```
                            ┌─────────────────────────────────────┐
                            │         USER REQUIREMENTS           │
                            │  budget, dates, preferences, etc.   │
                            └──────────────┬──────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────┐
                    │           PHASE 1: CANDIDATE GENERATION     │
                    │  Fan-out: Research N destinations parallel  │
                    └──────────────────────┬──────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              ▼                            ▼                            ▼
    ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
    │  destination-   │          │  destination-   │          │  destination-   │
    │   evaluate      │          │   evaluate      │          │   evaluate      │
    │   (Cabo)        │          │   (Hawaii)      │          │   (Costa Rica)  │
    └────────┬────────┘          └────────┬────────┘          └────────┬────────┘
             │                            │                            │
             └────────────────────────────┼────────────────────────────┘
                                          │
                    ┌─────────────────────▼──────────────────────┐
                    │        PHASE 2: CONSTRAINT FILTERING       │
                    │    feasibility-check on each candidate     │
                    │    (Binary: pass/fail on visa, dates, $)   │
                    └─────────────────────┬──────────────────────┘
                                          │
                    ┌─────────────────────▼──────────────────────┐
                    │      PHASE 3: EXPECTED VALUE RANKING       │
                    │                                            │
                    │  E[V] = P(good_weather) × quality_score    │
                    │         + value_for_money × budget_margin  │
                    │         - opportunity_cost(other_options)  │
                    │                                            │
                    │  Sort by E[V] descending → explore order   │
                    └─────────────────────┬──────────────────────┘
                                          │
                    ┌─────────────────────▼──────────────────────┐
                    │       PHASE 4: DEEP EXPLORATION (Loop)     │
                    │                                            │
                    │   FOR top_k candidates (highest E[V]):     │
                    │     └── option-explore (recursive L3)      │
                    │         ├── Get exact flight prices        │
                    │         ├── Get specific hotel options     │
                    │         ├── Calculate precise total cost   │
                    │         └── Refine quality score           │
                    │                                            │
                    │   EARLY TERMINATION condition:             │
                    │     IF marginal_improvement < search_cost  │
                    │     THEN stop exploring remaining options  │
                    └─────────────────────┬──────────────────────┘
                                          │
                    ┌─────────────────────▼──────────────────────┐
                    │      PHASE 5: GRADIENT DESCENT REFINE      │
                    │                                            │
                    │   Take best option, try local variations:  │
                    │     • Shift dates ±1-2 days               │
                    │     • Try nearby airports (OAK, SJC)       │
                    │     • Adjust hotel star rating             │
                    │                                            │
                    │   RECURSE: trip-optimize on variations     │
                    │   (with narrowed search space)             │
                    │                                            │
                    │   STOP when: Δcost/Δquality < threshold    │
                    └─────────────────────┬──────────────────────┘
                                          │
                    ┌─────────────────────▼──────────────────────┐
                    │           PHASE 6: FINAL COMPARISON        │
                    │                                            │
                    │   Present top 3 options on Pareto frontier │
                    │   with trade-off analysis                  │
                    └─────────────────────────────────────────────┘
```

## Microeconomic Concepts Applied

| Concept | Application in Algorithm |
|---------|-------------------------|
| **Expected Value** | E[V] = Σ P(outcome) × Value(outcome) for weather, availability |
| **Marginal Cost** | Cost of one more API call / exploration step |
| **Marginal Return** | Expected improvement in solution quality |
| **Opportunity Cost** | Value of best alternative foregone when choosing |
| **Gradient Descent** | Local search around best-so-far, following improvement gradient |
| **Early Termination** | Stop when E[marginal_return] < marginal_cost |
| **Pareto Frontier** | Present non-dominated options (no option strictly better on all dimensions) |

## Decision Criteria

### Binary Constraints (Hard Filters)

These eliminate options before expensive research:

```
feasibility_check(option, requirements):
    ├── visa_required == False           # Hard constraint
    ├── total_cost <= budget             # Hard constraint
    ├── dates ∈ available_dates          # Hard constraint
    └── flight_duration <= max_hours     # Hard constraint
```

### Continuous Scoring (Soft Ranking)

These determine exploration priority:

```
expected_value(option, preferences):
    │
    ├── weather_score = P(sunshine) × weather_weight
    │
    ├── value_score = log(quality) / log(cost) × value_weight
    │
    ├── convenience_score = 1 / (1 + flight_hours + transfers)
    │
    └── opportunity_cost = E[V](unexplored_options)

    RETURN: weather + value + convenience - opportunity_cost
```

## Compute Efficiency (Game Theory)

The algorithm uses **multi-armed bandit** intuition to balance exploration vs exploitation:

```
EXPLORATION vs EXPLOITATION trade-off:

Phase 1 (Early):    High exploration    → Fan-out to many destinations
Phase 4 (Middle):   Balanced            → Deep-dive top candidates only
Phase 5 (Late):     High exploitation   → Refine best option locally

STOPPING RULE (Early Termination):

  expected_improvement = best_unexplored_EV - current_best_EV
  search_cost = tokens_per_exploration × cost_per_token

  IF expected_improvement < search_cost × risk_aversion:
      STOP and return current_best
```

This prevents wasted API calls on low-potential options.

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `budget` | number | Yes | - | Maximum total trip cost in USD |
| `departure_city` | string | Yes | - | Origin city/airport code |
| `available_dates` | list | Yes | - | List of date ranges user can travel |
| `preferences` | object | No | `{}` | Weights for beach, food, culture, adventure |
| `max_flight_hours` | number | No | `12` | Maximum acceptable flight duration |
| `passport_country` | string | No | `"US"` | For visa requirement checking |
| `exploration_depth` | string | No | `"standard"` | quick / standard / thorough |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `recommendations` | list | Top 3 options on Pareto frontier |
| `best_option` | object | Highest expected value option with full details |
| `trade_off_analysis` | object | Comparison matrix showing what you gain/lose |
| `search_stats` | object | Candidates evaluated, API calls made, early terminations |

## Example Execution

```
User: "Plan a beach vacation from San Francisco, budget $2000,
       available March 15-22 or April 5-12"

trip-optimize execution:
│
├── PHASE 1: Generate 12 candidates
│   ├── destination-evaluate("Cabo San Lucas") → score: 0.82
│   ├── destination-evaluate("Hawaii - Maui") → score: 0.78
│   ├── destination-evaluate("Puerto Vallarta") → score: 0.75
│   ├── destination-evaluate("Costa Rica") → score: 0.71
│   └── ... (8 more in parallel)
│
├── PHASE 2: Filter by constraints
│   ├── ✓ Cabo: No visa, ~$1800 estimate, 3hr flight
│   ├── ✓ Maui: No visa, ~$1900 estimate, 5hr flight
│   ├── ✓ Puerto Vallarta: No visa, ~$1400 estimate, 3.5hr flight
│   ├── ✗ Bali: Visa on arrival OK but 18hr flight > max
│   └── ✓ Costa Rica: No visa, ~$1600 estimate, 6hr flight
│
├── PHASE 3: Rank by expected value
│   1. Puerto Vallarta: E[V] = 0.84 (best value-for-money)
│   2. Cabo: E[V] = 0.79 (higher quality, higher cost)
│   3. Costa Rica: E[V] = 0.73 (adventure bonus)
│   4. Maui: E[V] = 0.68 (beautiful but expensive)
│
├── PHASE 4: Deep exploration (top 3 only)
│   ├── option-explore("Puerto Vallarta", March 15-22)
│   │   ├── flight-search → $380 RT on Alaska
│   │   ├── hotel-search → $120/night beachfront
│   │   └── Total: $1,340 ✓ under budget
│   │
│   ├── option-explore("Cabo", March 15-22)
│   │   ├── flight-search → $420 RT on United
│   │   ├── hotel-search → $180/night resort
│   │   └── Total: $1,680 ✓ under budget
│   │
│   └── option-explore("Costa Rica", April 5-12)
│       ├── flight-search → $450 RT on Delta
│       ├── hotel-search → $100/night eco-lodge
│       └── Total: $1,350 ✓ under budget
│
│   [EARLY TERMINATION: Maui E[V] too low to justify search cost]
│
├── PHASE 5: Gradient descent on best option
│   ├── trip-optimize("Puerto Vallarta", March 14-21) → $1,290 (cheaper!)
│   ├── trip-optimize("Puerto Vallarta", March 16-23) → $1,380
│   └── trip-optimize("Puerto Vallarta", fly OAK) → $1,320
│
│   Best refinement: March 14-21, SFO, saves $50
│
└── PHASE 6: Final recommendations

    ┌─────────────────────────────────────────────────────────────┐
    │                    RECOMMENDATIONS                          │
    ├─────────────────────────────────────────────────────────────┤
    │ 🥇 BEST VALUE: Puerto Vallarta, March 14-21                 │
    │    Total: $1,290 | Weather: 92% sunshine | Beach: ⭐⭐⭐⭐⭐    │
    │    "Best bang for buck - $710 under budget"                 │
    │                                                             │
    │ 🥈 PREMIUM: Cabo San Lucas, March 15-22                     │
    │    Total: $1,680 | Weather: 95% sunshine | Beach: ⭐⭐⭐⭐⭐    │
    │    "Higher-end resorts, +$390 for luxury experience"        │
    │                                                             │
    │ 🥉 ADVENTURE: Costa Rica, April 5-12                        │
    │    Total: $1,350 | Weather: 85% sunshine | Nature: ⭐⭐⭐⭐⭐   │
    │    "Rainforests + beaches, different vibe"                  │
    └─────────────────────────────────────────────────────────────┘
```

## Composition Graph

```
trip-optimize (Level 3, READ)
├── trip-optimize         # Self-recursion for gradient descent refinement
├── option-explore        # L3 workflow for deep candidate exploration
├── destination-evaluate  # L2 composite for scoring
├── feasibility-check     # L2 composite for constraint filtering
└── route-price           # L2 composite for cost calculation
```

## Why This Showcases Composable Skills

| Feature | How Trip Optimizer Uses It |
|---------|---------------------------|
| **Fan-out parallelization** | Research 12 destinations simultaneously in Phase 1 |
| **Binary constraint filtering** | Eliminate options before expensive deep research |
| **Expected value ranking** | Prioritize exploration of high-potential options |
| **Self-recursion** | Gradient descent refinement in Phase 5 |
| **L3 → L3 composition** | `trip-optimize` calls `option-explore` for deep dives |
| **Early termination** | Stop when marginal return < marginal cost |
| **MECE compliance** | Clear level separation, no overlapping responsibilities |
| **Compute efficiency** | Game-theoretic stopping prevents wasted API calls |

## Notes

- All prices and availability are fetched in real-time via composed atomic skills
- The algorithm adapts exploration depth based on budget headroom
- Pareto frontier ensures no recommended option is strictly dominated
- Self-recursion depth is bounded to prevent infinite refinement loops
- Weather probabilities use historical data for the specific dates
