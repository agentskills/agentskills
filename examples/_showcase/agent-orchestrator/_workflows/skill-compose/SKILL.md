---
name: skill-compose
description: |
  Dynamically compose new skills from existing primitives based on user intent.
  Creates temporary or persistent skill definitions that chain existing skills
  to accomplish novel tasks.
level: 3
operation: WRITE
license: Apache-2.0
domain: agent-orchestration
composes:
  - skill-discover
  - skill-coherence-check
  - skill-graph-query
  - skill-registry-read
state_machine: true
---

# Skill Compose

Dynamically compose new skills from existing ones.

## When to Use

- User needs capability not directly available
- Multiple skills need chaining
- Creating reusable task patterns
- Building domain-specific workflows
- Automating repeated multi-step tasks

## State Machine

```
┌─────────────────┐
│  INTENT_PARSE   │ ← Understand what user needs
└────────┬────────┘
         │ Intent classified
         ▼
┌─────────────────┐
│ SKILL_DISCOVER  │ ← Find relevant primitives
└────────┬────────┘
         │ Candidates identified
         ▼
┌─────────────────┐
│  GRAPH_BUILD    │ ← Construct composition graph
└────────┬────────┘
         │ Graph valid
         ▼
┌─────────────────┐
│ SCHEMA_RESOLVE  │ ← Match inputs/outputs
└────────┬────────┘
         │ Schemas compatible
         ▼
┌─────────────────┐
│ COHERENCE_CHECK │ ← Validate composition
└────────┬────────┘
         │ Checks passed
         ▼
┌─────────────────┐
│ [HUMAN] REVIEW  │ ← User approves composition
└────────┬────────┘
         │ Approved
         ▼
┌─────────────────┐
│ SKILL_GENERATE  │ ← Create skill definition
└────────┬────────┘
         │ Skill created
         ▼
┌─────────────────┐
│   REGISTERED    │ ✓ Skill available for use
└─────────────────┘
```

## Composition Patterns

### Sequential Chain
```
A → B → C

customer-compliance-report =
  client-data-read → compliance-check → report-generate
```

### Parallel Fan-Out
```
    ┌→ B ─┐
A ──┼→ C ─┼→ E
    └→ D ─┘

multi-portfolio-analyse =
  holdings-ingest →
    [risk-metrics-calculate, benchmark-compare, tax-impact-estimate]
  → aggregate-results
```

### Conditional Branch
```
A → (condition) → B or C

smart-alert =
  threshold-check →
    (exceeded?) → alert-send
    (normal) → log-record
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | Yes | What the new skill should do |
| `name` | string | No | Name for new skill (auto-generated if omitted) |
| `persist` | boolean | No | Save skill permanently (default: false) |
| `domain` | string | No | Target domain for skill |
| `test_run` | boolean | No | Dry run to verify composition |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `skill_definition` | object | Complete skill YAML/markdown |
| `composition_graph` | object | Visual representation |
| `level` | number | Determined skill level |
| `validation` | object | Coherence check results |
| `file_path` | string | Path if persisted |

## Usage

```
Compose a skill that reads customer data, checks compliance, and generates a PDF report
```

```
Create a skill to analyse all portfolios in parallel and aggregate results
```

```
Build a skill that monitors drift and sends alerts when thresholds exceeded
```

## Example: Sequential Composition

**Input:**
```
Create a skill that reads customer data, checks compliance, and generates a report
```

**Generated Skill:**
```yaml
---
name: customer-compliance-report
description: |
  Read customer data, verify compliance status, and generate
  a formatted compliance report.
level: 2
operation: READ
domain: financial-advisor
composes:
  - client-data-read
  - compliance-check
  - document-generate
---

# Customer Compliance Report

Generate compliance reports for customers.

## Workflow

1. Read customer profile → client-data-read
2. Check compliance status → compliance-check
3. Generate report → document-generate

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Customer identifier |
| `report_format` | string | No | pdf, docx, md (default: pdf) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `report_url` | string | Generated report location |
| `compliance_status` | string | passed, failed, review |
| `issues` | object[] | Any compliance issues found |
```

## Example: Parallel Composition

**Input:**
```
Analyse risk for multiple portfolios in parallel
```

**Generated Skill:**
```yaml
---
name: multi-portfolio-risk-analyse
description: |
  Analyse risk metrics for multiple portfolios in parallel
  and aggregate results into a comparison report.
level: 3
operation: READ
domain: portfolio-manager
composes:
  - holdings-ingest
  - risk-metrics-calculate
  - risk-metrics-calculate  # Parallel instances
  - scenario-analyse
state_machine: true
---
```

## Human Checkpoint

Before generating the skill, present to user:

```
┌─────────────────────────────────────────────────────────┐
│           SKILL COMPOSITION REVIEW                      │
├─────────────────────────────────────────────────────────┤
│ Name: customer-compliance-report                        │
│ Level: 2 (Composite)                                    │
│ Operation: READ                                         │
│                                                         │
│ Composition:                                            │
│   1. client-data-read (L1) → customer profile          │
│   2. compliance-check (L1) → compliance status         │
│   3. document-generate (L1) → PDF report               │
│                                                         │
│ Schema Flow:                                            │
│   client_id → [client data] → [compliance] → report    │
│                                                         │
│ Validation: ✓ Passed coherence check                   │
├─────────────────────────────────────────────────────────┤
│ [Approve] [Modify] [Cancel]                             │
└─────────────────────────────────────────────────────────┘
```

## Notes

- Composed skills inherit the highest level of their components
- READ + WRITE composition → WRITE operation
- Persist frequently-used compositions
- Generated skills go to skills/_generated/
- Test run validates without creating file
