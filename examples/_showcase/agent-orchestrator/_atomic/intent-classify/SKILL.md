---
name: intent-classify
description: Classify user intent into operation types, domains, and action categories to enable skill matching and disambiguation.
level: 1
operation: TRANSFORM
license: Apache-2.0
domain: agent-orchestration
---

# Intent Classify

Classify user intent to enable intelligent skill discovery and routing.

## When to Use

- Parsing natural language requests
- Determining READ vs WRITE intent
- Identifying target domain
- Detecting ambiguous or multi-intent requests
- Routing to appropriate skill discovery

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_input` | string | Yes | Raw user request text |
| `context` | object | No | Conversation context (previous intents) |
| `available_domains` | string[] | No | Limit to specific domains |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `primary_intent` | object | Main classified intent |
| `secondary_intents` | object[] | Additional detected intents |
| `confidence` | number | Classification confidence (0-1) |
| `ambiguity_flags` | string[] | Detected ambiguities |
| `suggested_clarifications` | string[] | Questions to resolve ambiguity |

## Intent Schema

```json
{
  "operation": "READ",           // READ, WRITE, TRANSFORM
  "action": "analyse",           // verb category
  "domain": "portfolio-manager", // target domain
  "entities": [
    {"type": "portfolio", "value": "retirement-fund"},
    {"type": "metric", "value": "risk"}
  ],
  "modifiers": {
    "temporal": "current",       // current, historical, projected
    "scope": "full",             // full, partial, summary
    "urgency": "normal"          // normal, urgent, background
  }
}
```

## Operation Classification Rules

| Signal | Operation | Examples |
|--------|-----------|----------|
| read, get, show, list, find, check, analyse | READ | "show my portfolio", "check risk" |
| create, add, update, send, execute, submit | WRITE | "send email", "execute trade" |
| calculate, transform, convert, format | TRANSFORM | "calculate returns", "format report" |

## Ambiguity Detection

Ambiguity is flagged when:

1. **Multiple domains match**: "update the data" (which data?)
2. **Missing required context**: "send it" (send what?)
3. **Conflicting signals**: "read and update" (two operations)
4. **Vague entities**: "check the thing" (which thing?)
5. **Implicit assumptions**: "do the usual" (what's usual?)

## Usage

```
Classify: "I need to rebalance my retirement portfolio based on new risk tolerance"
```

```
Classify: "Update the data" (should flag ambiguity)
```

```
Classify: "Show me customer intel and draft a follow-up email"
```

## Example Response

```json
{
  "primary_intent": {
    "operation": "WRITE",
    "action": "rebalance",
    "domain": "portfolio-manager",
    "entities": [
      {"type": "portfolio", "value": "retirement"},
      {"type": "parameter", "value": "risk-tolerance"}
    ],
    "modifiers": {
      "temporal": "current",
      "scope": "full"
    }
  },
  "secondary_intents": [],
  "confidence": 0.92,
  "ambiguity_flags": [],
  "suggested_clarifications": []
}
```

## Example with Ambiguity

```json
{
  "primary_intent": {
    "operation": "WRITE",
    "action": "update",
    "domain": null,
    "entities": [
      {"type": "unknown", "value": "data"}
    ]
  },
  "confidence": 0.34,
  "ambiguity_flags": [
    "domain_ambiguous",
    "entity_vague"
  ],
  "suggested_clarifications": [
    "Which data would you like to update? (customer data, portfolio data, market data)",
    "Could you specify which record or dataset?"
  ]
}
```

## Notes

- Confidence < 0.7 should trigger disambiguation
- Multi-intent requests should be decomposed
- Context from conversation history improves accuracy
