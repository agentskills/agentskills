---
name: skill-registry-read
description: Read skill definitions from the skill registry. Returns skill metadata including name, level, operation type, inputs, outputs, and composition relationships.
level: 1
operation: READ
license: Apache-2.0
domain: agent-orchestration
tool_discovery:
  filesystem:
    prefer: [glob-search, file-read]
    fallback: shell-find
---

# Skill Registry Read

Read skill definitions from the registry to understand available capabilities.

## When to Use

- Discovering what skills exist in a domain
- Understanding a skill's inputs and outputs
- Finding skills by operation type (READ/WRITE/TRANSFORM)
- Building skill composition graphs

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `skill_name` | string | No | Specific skill to read (if omitted, lists all) |
| `domain` | string | No | Filter by domain (e.g., "portfolio-manager") |
| `level` | number | No | Filter by level (1, 2, or 3) |
| `operation` | string | No | Filter by operation (READ, WRITE, TRANSFORM) |
| `include_graph` | boolean | No | Include composition relationships |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `skills` | object[] | List of skill definitions |
| `count` | number | Number of skills found |
| `domains` | string[] | Unique domains in results |
| `levels` | object | Count by level |

## Skill Definition Schema

```json
{
  "name": "risk-metrics-calculate",
  "description": "Calculate portfolio risk metrics",
  "level": 1,
  "operation": "READ",
  "domain": "portfolio-manager",
  "inputs": [
    {"name": "holdings", "type": "object[]", "required": true}
  ],
  "outputs": [
    {"name": "var", "type": "number"},
    {"name": "sharpe_ratio", "type": "number"}
  ],
  "composes": [],
  "composed_by": ["risk-profile-estimate", "scenario-analyse"]
}
```

## Usage

```
List all skills in the portfolio-manager domain
```

```
Find all Level 2 composite skills with WRITE operation
```

```
Get the full definition of the rebalance-execute workflow
```

## Example Response

```json
{
  "skills": [
    {
      "name": "holdings-ingest",
      "level": 1,
      "operation": "READ",
      "domain": "portfolio-manager"
    },
    {
      "name": "risk-metrics-calculate",
      "level": 1,
      "operation": "READ",
      "domain": "portfolio-manager"
    }
  ],
  "count": 2,
  "domains": ["portfolio-manager"],
  "levels": {"1": 2, "2": 0, "3": 0}
}
```

## Notes

- Registry is read from `examples/_showcase/*/` directories
- Each skill must have a SKILL.md with YAML frontmatter
- Composition graph built from `composes` field in frontmatter
