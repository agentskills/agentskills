---
name: skill-disambiguate
description: |
  Flag when skill selection is unclear and generate clarification prompts.
  Detects ambiguity in user requests and provides structured options for resolution.
level: 2
operation: READ
license: Apache-2.0
domain: agent-orchestration
composes:
  - intent-classify
  - skill-registry-read
---

# Skill Disambiguate

Detect and resolve ambiguous skill selections.

## When to Use

- Multiple skills match with similar confidence
- User intent is vague or underspecified
- Domain cannot be determined
- Conflicting signals in request
- Missing required context

## Composition Graph

```
skill-disambiguate (Level 2, READ)
├── intent-classify        # L1: Detect ambiguity signals
└── skill-registry-read    # L1: Find competing matches
```

## Ambiguity Types

| Type | Description | Example |
|------|-------------|---------|
| `domain_ambiguous` | Multiple domains match | "update the data" |
| `entity_vague` | Target not specific | "check the thing" |
| `multi_intent` | Multiple operations | "read and update" |
| `missing_context` | Required info absent | "send it" |
| `implicit_assumption` | Unstated expectations | "do the usual" |
| `conflicting_signals` | Contradictory cues | "quickly but thoroughly" |

## Workflow

```
1. DETECT AMBIGUITY
   │
   ├── Confidence < threshold (0.7)
   ├── Multiple high-scoring matches
   ├── Missing required parameters
   └── Conflicting operation signals
   │
   ▼
2. CLASSIFY AMBIGUITY TYPE
   │
   ├── Identify primary ambiguity
   ├── Detect secondary ambiguities
   └── Assess resolution complexity
   │
   ▼
3. GENERATE CLARIFICATION
   │
   ├── Build structured options
   ├── Order by likelihood
   ├── Include context hints
   └── Format for user presentation
   │
   ▼
4. RETURN DISAMBIGUATION PROMPT
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_input` | string | Yes | Ambiguous user request |
| `matched_skills` | object[] | No | Previously matched skills |
| `context` | object | No | Conversation context |
| `max_options` | number | No | Max clarification options (default: 4) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `is_ambiguous` | boolean | Whether disambiguation needed |
| `ambiguity_types` | string[] | Types of ambiguity detected |
| `competing_skills` | object[] | Skills with similar scores |
| `clarification` | object | Structured clarification prompt |
| `confidence_gap` | number | Difference between top matches |

## Clarification Schema

```json
{
  "clarification": {
    "question": "Which data would you like to update?",
    "options": [
      {
        "label": "Customer data",
        "skill": "client-data-update",
        "context": "Update customer profiles in CRM"
      },
      {
        "label": "Portfolio holdings",
        "skill": "holdings-ingest",
        "context": "Refresh current investment positions"
      },
      {
        "label": "Market data",
        "skill": "market-data-fetch",
        "context": "Fetch latest prices and quotes"
      }
    ],
    "allow_multiple": false,
    "allow_custom": true,
    "custom_prompt": "Or describe what you'd like to update:"
  }
}
```

## Usage

```
Disambiguate: "update the data"
```

```
Clarify: "send it to them"
```

```
Resolve: "check the status and fix any issues"
```

## Example Response

```json
{
  "user_input": "update the data",
  "is_ambiguous": true,
  "ambiguity_types": ["domain_ambiguous", "entity_vague"],
  "competing_skills": [
    {
      "name": "client-data-update",
      "domain": "financial-advisor",
      "score": 0.42
    },
    {
      "name": "holdings-ingest",
      "domain": "portfolio-manager",
      "score": 0.38
    },
    {
      "name": "market-data-fetch",
      "domain": "portfolio-manager",
      "score": 0.35
    }
  ],
  "confidence_gap": 0.04,
  "clarification": {
    "question": "Which data would you like to update?",
    "options": [
      {"label": "Customer/client data", "skill": "client-data-update"},
      {"label": "Portfolio holdings", "skill": "holdings-ingest"},
      {"label": "Market prices", "skill": "market-data-fetch"}
    ],
    "allow_multiple": false,
    "allow_custom": true
  }
}
```

## Multi-Intent Example

```json
{
  "user_input": "check the portfolio and send an update to the client",
  "is_ambiguous": true,
  "ambiguity_types": ["multi_intent"],
  "detected_intents": [
    {"operation": "READ", "action": "check", "skill": "portfolio-summarise"},
    {"operation": "WRITE", "action": "send", "skill": "email-compose"}
  ],
  "clarification": {
    "question": "This involves two actions. How would you like to proceed?",
    "options": [
      {"label": "Do both in sequence", "approach": "chain"},
      {"label": "Just check the portfolio", "skill": "portfolio-summarise"},
      {"label": "Just send the update", "skill": "email-compose"}
    ]
  }
}
```

## Resolution Strategies

| Ambiguity | Strategy |
|-----------|----------|
| domain_ambiguous | Present domain options |
| entity_vague | Ask for specific target |
| multi_intent | Offer sequence or selection |
| missing_context | Request missing info |
| implicit_assumption | Make assumptions explicit |

## Notes

- Never proceed with ambiguous requests for WRITE operations
- READ operations can proceed with best guess + confirmation
- Track disambiguation patterns to improve intent classification
- User can always provide custom clarification
