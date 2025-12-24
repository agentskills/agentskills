---
name: skill-discover
description: |
  Discover relevant skills based on user intent. Combines intent classification
  with skill registry lookup to find the best matching skills for a given request.
level: 2
operation: READ
license: Apache-2.0
domain: agent-orchestration
composes:
  - intent-classify
  - skill-registry-read
  - skill-graph-query
---

# Skill Discover

Find the right skills for a user's intent.

## When to Use

- User makes a natural language request
- Need to find skills in an unfamiliar domain
- Exploring available capabilities
- Building skill recommendations
- Routing requests to appropriate handlers

## Composition Graph

```
skill-discover (Level 2, READ)
├── intent-classify        # L1: Parse user intent
├── skill-registry-read    # L1: Read available skills
└── skill-graph-query      # L1: Find related skills
```

## Workflow

```
1. CLASSIFY USER INTENT
   │
   ├── Parse natural language request
   ├── Extract operation type (READ/WRITE/TRANSFORM)
   ├── Identify domain signals
   └── Detect entities and modifiers
   │
   ▼
2. SEARCH SKILL REGISTRY
   │
   ├── Filter by operation type
   ├── Filter by domain (if detected)
   ├── Match on skill names and descriptions
   └── Score relevance
   │
   ▼
3. EXPAND WITH GRAPH
   │
   ├── Find composed-by relationships
   ├── Suggest related skills
   └── Identify skill chains
   │
   ▼
4. RANK AND RETURN
   │
   ├── Sort by relevance score
   ├── Group by confidence tier
   └── Include usage hints
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_input` | string | Yes | Natural language request |
| `context` | object | No | Previous conversation context |
| `max_results` | number | No | Maximum skills to return (default: 5) |
| `include_related` | boolean | No | Include related skills (default: true) |
| `min_confidence` | number | No | Minimum confidence threshold (default: 0.5) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `matched_skills` | object[] | Skills matching the intent |
| `related_skills` | object[] | Related skills via composition |
| `intent` | object | Classified intent details |
| `confidence` | number | Overall match confidence |
| `disambiguation_needed` | boolean | Whether clarification required |

## Skill Match Schema

```json
{
  "skill": {
    "name": "risk-metrics-calculate",
    "level": 1,
    "operation": "READ",
    "domain": "portfolio-manager",
    "description": "Calculate portfolio risk metrics"
  },
  "relevance_score": 0.92,
  "match_reasons": [
    "operation_match: READ",
    "domain_match: portfolio",
    "entity_match: risk"
  ],
  "usage_hint": "Use this to calculate VaR, Sharpe ratio, and volatility"
}
```

## Usage

```
Find skills for: "I need to analyse my portfolio's risk exposure"
```

```
What skills help with: "sending customer updates via email"
```

```
Discover skills for: "rebalancing investments"
```

## Example Response

```json
{
  "user_input": "I need to analyse my portfolio's risk exposure",
  "intent": {
    "operation": "READ",
    "action": "analyse",
    "domain": "portfolio-manager",
    "entities": [
      {"type": "portfolio", "value": "portfolio"},
      {"type": "metric", "value": "risk"}
    ]
  },
  "matched_skills": [
    {
      "skill": {
        "name": "risk-metrics-calculate",
        "level": 1,
        "operation": "READ"
      },
      "relevance_score": 0.95,
      "match_reasons": ["operation_match", "entity_match: risk"]
    },
    {
      "skill": {
        "name": "scenario-analyse",
        "level": 2,
        "operation": "READ"
      },
      "relevance_score": 0.88,
      "match_reasons": ["operation_match", "action_match: analyse"]
    },
    {
      "skill": {
        "name": "risk-profile-estimate",
        "level": 2,
        "operation": "READ"
      },
      "relevance_score": 0.82,
      "match_reasons": ["entity_match: risk", "domain_match"]
    }
  ],
  "related_skills": [
    {
      "name": "portfolio-summarise",
      "relationship": "often_used_with",
      "reason": "Provides portfolio context for risk analysis"
    }
  ],
  "confidence": 0.91,
  "disambiguation_needed": false
}
```

## Low Confidence Example

```json
{
  "user_input": "update the data",
  "intent": {
    "operation": "WRITE",
    "action": "update",
    "domain": null,
    "entities": [{"type": "unknown", "value": "data"}]
  },
  "matched_skills": [
    {"skill": {"name": "client-data-update"}, "relevance_score": 0.4},
    {"skill": {"name": "holdings-ingest"}, "relevance_score": 0.35},
    {"skill": {"name": "market-data-fetch"}, "relevance_score": 0.32}
  ],
  "confidence": 0.38,
  "disambiguation_needed": true,
  "clarification_prompt": "Which data would you like to update?\n- Customer/client data\n- Portfolio holdings\n- Market data"
}
```

## Notes

- Confidence < 0.7 triggers disambiguation
- Multiple high-confidence matches suggest composite skill
- Related skills help build complete workflows
