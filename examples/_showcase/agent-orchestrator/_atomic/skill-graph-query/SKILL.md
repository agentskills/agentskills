---
name: skill-graph-query
description: Query the skill composition graph to find relationships, dependencies, and composition paths between skills.
level: 1
operation: READ
license: Apache-2.0
domain: agent-orchestration
---

# Skill Graph Query

Query skill composition relationships to understand how skills connect.

## When to Use

- Finding all skills that compose a given skill
- Finding all skills composed by a given skill
- Detecting circular dependencies
- Finding composition paths between skills
- Visualising skill hierarchies

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `skill_name` | string | No | Skill to query relationships for |
| `query_type` | string | Yes | Type: ancestors, descendants, path, cycles |
| `target_skill` | string | No | Target for path queries |
| `max_depth` | number | No | Maximum traversal depth (default: 5) |
| `domain` | string | No | Limit to specific domain |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `nodes` | object[] | Skills in result set |
| `edges` | object[] | Composition relationships |
| `path` | string[] | Path between skills (if path query) |
| `has_cycles` | boolean | Whether cycles detected |
| `depth` | number | Maximum depth traversed |

## Query Types

### ancestors
Find all skills that the given skill composes (direct and transitive):
```
rebalance-execute → ancestors
├── trade-list-generate (L2)
│   ├── holdings-ingest (L1)
│   └── constraint-validate (L1)
├── suitability-assess (L2)
│   ├── risk-profile-estimate (L2)
│   │   └── risk-metrics-calculate (L1)
│   └── goal-allocation-generate (L2)
└── ...
```

### descendants
Find all skills that compose the given skill:
```
risk-metrics-calculate ← descendants
├── risk-profile-estimate (L2)
├── scenario-analyse (L2)
└── annual-portfolio-review (L3)
```

### path
Find composition path between two skills:
```
path(annual-portfolio-review → holdings-ingest)
= [annual-portfolio-review, portfolio-summarise, holdings-ingest]
```

### cycles
Detect circular dependencies (excluding self-recursion):
```
cycles(domain: "portfolio-manager")
= [] # No invalid cycles
```

## Usage

```
Find all skills that rebalance-execute depends on
```

```
What skills use risk-metrics-calculate?
```

```
Is there a path from trip-optimize to flight-search?
```

## Example Response

```json
{
  "query_type": "ancestors",
  "skill_name": "rebalance-execute",
  "nodes": [
    {"name": "trade-list-generate", "level": 2},
    {"name": "holdings-ingest", "level": 1},
    {"name": "constraint-validate", "level": 1}
  ],
  "edges": [
    {"from": "rebalance-execute", "to": "trade-list-generate"},
    {"from": "trade-list-generate", "to": "holdings-ingest"},
    {"from": "trade-list-generate", "to": "constraint-validate"}
  ],
  "depth": 2,
  "has_cycles": false
}
```

## Notes

- Self-recursion (skill composing itself) is allowed for L3 workflows
- Cross-level composition must respect: L3→L2→L1 hierarchy
- L3→L3 composition allowed for workflow orchestration
