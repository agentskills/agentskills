---
name: activity-search
description: Search for activities and attractions at a destination matching user preferences.
level: 1
operation: READ
license: Apache-2.0
---

# Activity Search

A Level 1 atomic skill that finds things to do at a destination.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination` | string | Yes | City or region |
| `preferences` | list | No | Activity types (beach, culture, adventure, food) |
| `dates` | object | No | For seasonal activity availability |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `activities` | list | Available activities |
| `match_score` | number | How well activities match preferences |

## Example

```
activity-search("Puerto Vallarta", preferences=["beach", "food"]):

RETURN:
  activities:
    - name: "Playa de los Muertos"
      type: "beach"
      rating: 4.5
    - name: "Malecón Boardwalk"
      type: "sightseeing"
      rating: 4.7
    - name: "Street Food Tour"
      type: "food"
      rating: 4.8
  match_score: 0.85
```
