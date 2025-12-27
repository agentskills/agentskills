---
name: skill-coherence-check
description: |
  Validate skill consistency and detect conflicts. Ensures skills follow
  architectural rules, level constraints, and naming conventions.
level: 2
operation: READ
license: Apache-2.0
domain: agent-orchestration
composes:
  - skill-registry-read
  - skill-graph-query
---

# Skill Coherence Check

Validate skill consistency across the registry.

## When to Use

- After creating or modifying skills
- Before merging skill changes
- During CI/CD validation
- Periodic registry audits
- Detecting architectural drift

## Composition Graph

```
skill-coherence-check (Level 2, READ)
├── skill-registry-read    # L1: Load all skill definitions
└── skill-graph-query      # L1: Analyse composition relationships
```

## Validation Rules

### Level Constraints

| Rule | Description | Severity |
|------|-------------|----------|
| L001 | L1 skills must not compose other skills | ERROR |
| L002 | L2 skills must compose at least one L1 | ERROR |
| L003 | L3 skills must have state_machine or composes | ERROR |
| L004 | Level must match directory (_atomic, _composite, _workflows) | ERROR |
| L005 | Cross-level composition: L3→L2→L1 only | WARNING |

### Naming Conventions

| Rule | Description | Severity |
|------|-------------|----------|
| N001 | Names must be kebab-case | ERROR |
| N002 | Name must match directory name | ERROR |
| N003 | Operation verbs should match: read→READ, update→WRITE | WARNING |
| N004 | Domain-specific prefixes encouraged | INFO |

### Composition Integrity

| Rule | Description | Severity |
|------|-------------|----------|
| C001 | All composed skills must exist | ERROR |
| C002 | No circular dependencies (except self-recursion) | ERROR |
| C003 | Self-recursion only for L3 workflows | WARNING |
| C004 | Composed skills should be lower level | WARNING |

### Schema Consistency

| Rule | Description | Severity |
|------|-------------|----------|
| S001 | Required frontmatter fields present | ERROR |
| S002 | Input/output schemas well-formed | WARNING |
| S003 | Schema types consistent across compositions | WARNING |
| S004 | Output of composed skill matches expected input | INFO |

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `skill_name` | string | No | Check specific skill (or all if omitted) |
| `domain` | string | No | Check specific domain |
| `severity_threshold` | string | No | Minimum severity to report (default: WARNING) |
| `fix_suggestions` | boolean | No | Include auto-fix suggestions |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `valid` | boolean | Whether all checks passed |
| `errors` | object[] | ERROR severity issues |
| `warnings` | object[] | WARNING severity issues |
| `info` | object[] | INFO severity issues |
| `summary` | object | Count by severity |
| `skills_checked` | number | Total skills validated |

## Issue Schema

```json
{
  "rule": "L001",
  "severity": "ERROR",
  "skill": "market-data-fetch",
  "message": "L1 skill composes other skills",
  "details": "L1 skills should be atomic and not compose others",
  "location": {
    "file": "examples/_showcase/portfolio-manager/_atomic/market-data-fetch/SKILL.md",
    "line": 8
  },
  "fix_suggestion": "Remove 'composes' field or move to _composite"
}
```

## Usage

```
Check coherence of all skills in portfolio-manager domain
```

```
Validate the newly created customer-intel skill
```

```
Run full registry coherence check
```

## Example Response

```json
{
  "valid": false,
  "skills_checked": 52,
  "summary": {
    "errors": 2,
    "warnings": 5,
    "info": 8
  },
  "errors": [
    {
      "rule": "C001",
      "severity": "ERROR",
      "skill": "soa-prepare",
      "message": "Composed skill 'document-format' does not exist",
      "fix_suggestion": "Create document-format skill or remove from composes"
    },
    {
      "rule": "L004",
      "severity": "ERROR",
      "skill": "risk-analyse",
      "message": "Skill in _atomic has level: 2",
      "fix_suggestion": "Move to _composite or change level to 1"
    }
  ],
  "warnings": [
    {
      "rule": "N003",
      "severity": "WARNING",
      "skill": "portfolio-read",
      "message": "Skill name suggests READ but operation is TRANSFORM",
      "fix_suggestion": "Change operation to READ or rename skill"
    }
  ]
}
```

## Clean Check Example

```json
{
  "valid": true,
  "skills_checked": 52,
  "summary": {
    "errors": 0,
    "warnings": 0,
    "info": 3
  },
  "info": [
    {
      "rule": "N004",
      "severity": "INFO",
      "skill": "calculate-metrics",
      "message": "Consider domain prefix: portfolio-calculate-metrics"
    }
  ]
}
```

## Notes

- Run coherence check before every commit
- ERROR severity blocks merges
- WARNING severity should be reviewed
- INFO severity is advisory only
- Use --fix to auto-apply safe fixes
