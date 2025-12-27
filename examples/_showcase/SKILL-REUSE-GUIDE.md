# Skill Reuse Patterns

This guide explains how to reuse, extend, and compose skills from the showcase library.

## Table of Contents

1. [Understanding Skill Levels](#understanding-skill-levels)
2. [Composition Patterns](#composition-patterns)
3. [Extending Skills](#extending-skills)
4. [Creating Domain-Specific Showcases](#creating-domain-specific-showcases)
5. [Best Practices](#best-practices)

---

## Understanding Skill Levels

### Level 1: Atomic Skills

Atomic skills are the building blocks. They perform single operations with no composition.

```yaml
# Characteristics
- Single responsibility
- No composes field
- Direct tool interaction
- Reusable across domains

# Example: market-data-fetch
level: 1
operation: READ
tools:
  preferred: [yahoo-finance, alpha-vantage]
  fallback: web-scrape
```

**When to reuse L1 skills:**
- Need raw data access (prices, client info, calendar)
- Need external tool interaction (send email, execute trade)
- Building a new L2 or L3 skill

### Level 2: Composite Skills

Composite skills combine atomics and add domain logic.

```yaml
# Characteristics
- Combines 2+ L1 skills
- Adds business logic
- Produces derived outputs
- Domain-specific but reusable

# Example: portfolio-summarise
level: 2
composes:
  - holdings-ingest    # L1
  - market-data-fetch  # L1
```

**When to reuse L2 skills:**
- Need a complete unit of analysis
- Building a workflow
- Want consistent domain logic

### Level 3: Workflow Skills

Workflows orchestrate multiple skills with state machines.

```yaml
# Characteristics
- State machine with transitions
- Human checkpoints for approvals
- Error handling and recovery
- End-to-end process automation
```

---

## Composition Patterns

### Pattern 1: Sequential Composition

Skills execute one after another, each using the previous output.

```yaml
workflow:
  step_1:
    skill: holdings-ingest
    output: holdings
    next: step_2

  step_2:
    skill: market-data-fetch
    input:
      securities: ${holdings.security_ids}
    output: prices
    next: step_3

  step_3:
    skill: portfolio-summarise
    input:
      holdings: ${holdings}
      prices: ${prices}
```

### Pattern 2: Parallel Composition

Independent skills run concurrently for better performance.

```yaml
workflow:
  step_1:
    parallel:
      - skill: holdings-ingest
        output: holdings
      - skill: client-goals-read
        output: goals
      - skill: market-benchmarks-fetch
        output: benchmarks
    next: step_2

  step_2:
    skill: analyse-with-all-data
    input:
      holdings: ${parallel.holdings}
      goals: ${parallel.goals}
      benchmarks: ${parallel.benchmarks}
```

### Pattern 3: Conditional Composition

Choose skills based on runtime conditions.

```yaml
workflow:
  step_1:
    skill: assess-situation
    output: assessment
    decision:
      - condition: assessment.requires_rebalance
        next: rebalance_flow
      - condition: assessment.requires_review
        next: review_flow
      - default:
        next: monitoring_flow
```

### Pattern 4: Recursive Composition

Skills can call themselves for iterative refinement.

```yaml
# Example: option-explore (from trip-optimizer)
composes:
  - option-explore  # Self-reference for iteration
  - route-price
  - destination-evaluate
```

---

## Extending Skills

### Approach 1: Wrapper Skills

Create a new skill that wraps an existing one with additional logic.

```yaml
# Original: portfolio-summarise (generic)
# Extended: portfolio-summarise-au (Australia-specific)

name: portfolio-summarise-au
level: 2

composes:
  - portfolio-summarise  # Reuse existing

# Add Australia-specific logic
pre_processing:
  - Convert currencies to AUD
  - Apply franking credit calculations

post_processing:
  - Add superannuation breakdown
  - Flag SMSF compliance issues
```

### Approach 2: Configuration Injection

Make skills configurable to support multiple use cases.

```yaml
# Generic skill with configuration
name: alert-send
level: 1

input:
  alert: object
  config:
    channels:
      type: array
      default: [email]
      options: [email, slack, sms, push]
    templates:
      type: object
      description: Override default templates
```

### Approach 3: Skill Inheritance (Conceptual)

Create skill variants that share base definitions.

```
base-portfolio-review/
├── SKILL.md          # Base skill definition
└── variants/
    ├── quarterly/
    │   └── SKILL.md  # extends: ../SKILL.md
    ├── annual/
    │   └── SKILL.md  # extends: ../SKILL.md
    └── triggered/
        └── SKILL.md  # extends: ../SKILL.md
```

---

## Creating Domain-Specific Showcases

### Step 1: Identify Core Entities

```
Domain: Real Estate Investment
├── Properties (like Holdings)
├── Tenants (like Clients)
├── Leases (like Contracts)
└── Market Data (like Prices)
```

### Step 2: Map to Skill Levels

```
L1 Atomic:
├── property-data-read
├── tenant-data-read
├── market-rent-fetch
├── lease-document-read
└── alert-send (reuse)

L2 Composite:
├── property-valuation
├── rental-yield-calculate
├── vacancy-risk-assess
└── portfolio-summarise (adapt)

L3 Workflows:
├── tenant-onboard
├── lease-renewal
├── property-acquisition
└── annual-property-review
```

### Step 3: Identify Reusable Skills

Skills that can be reused across domains:

| Generic Skill | Domain Adaptation |
|--------------|-------------------|
| alert-send | Same - notifications are universal |
| holdings-ingest | Adapt → property-data-read |
| portfolio-summarise | Adapt → property-portfolio-summarise |
| annual-review | Adapt → annual-property-review |

### Step 4: Create the Showcase

```
examples/_showcase/
└── real-estate-investor/
    ├── README.md
    ├── _atomic/
    │   ├── property-data-read/
    │   ├── tenant-data-read/
    │   └── market-rent-fetch/
    ├── _composite/
    │   ├── property-valuation/
    │   └── rental-yield-calculate/
    └── _workflows/
        ├── tenant-onboard/
        └── lease-renewal/
```

---

## Best Practices

### 1. Start with Atomics

When building a new domain showcase:
1. Identify data sources → Create L1 READ skills
2. Identify actions → Create L1 WRITE skills
3. Compose them into L2 skills
4. Orchestrate with L3 workflows

### 2. Keep Atomics Pure

```yaml
# GOOD: Single responsibility
name: market-data-fetch
operation: READ
# Only fetches data, no analysis

# BAD: Mixed responsibilities
name: market-data-fetch-and-analyse
operation: READ  # Should be TRANSFORM
```

### 3. Document Tool Alternatives

```yaml
tools:
  preferred:
    - name: primary-api
      operations: [read]
  fallback:
    - name: backup-api
      description: "Used when primary is unavailable"
    - name: web-scrape
      description: "Last resort for missing data"
```

### 4. Use Consistent Schemas

Reuse schema patterns across skills:

```yaml
# Standard holdings schema (use everywhere)
holdings:
  type: array
  items:
    security_id: string
    quantity: number
    value: number
    weight: number
```

### 5. Human Checkpoints for WRITE Operations

```yaml
# Any skill that modifies data or sends communications
operation: WRITE
requires_approval: true
human_checkpoints: [before_execute]
```

### 6. Test Composition Chains

Create tests that verify:
- L2 skills correctly compose L1 skills
- L3 workflows compose L2 skills
- State transitions work as documented

---

## Examples of Cross-Showcase Reuse

### Reusing portfolio-manager skills in financial-advisor

```yaml
# financial-advisor/advice-delivery workflow
composes:
  # From financial-advisor showcase
  - soa-prepare
  - compliance-check

  # Reused from portfolio-manager showcase
  - portfolio-summarise      # Imported
  - risk-profile-estimate    # Imported
  - trade-list-generate      # Imported
```

### Creating a unified skill registry

```yaml
# config/skill-registry.yaml
skills:
  core:
    - alert-send
    - market-data-fetch
    - holdings-ingest

  portfolio-management:
    - portfolio-summarise
    - risk-profile-estimate
    - trade-list-generate

  financial-advisory:
    - soa-prepare
    - compliance-check
    - client-data-read

# Reference in compositions
composes:
  - $ref: core/alert-send
  - $ref: portfolio-management/trade-list-generate
```

---

## Checklist for Skill Reuse

Before reusing a skill, verify:

- [ ] Level matches your needs (L1 for data, L2 for analysis, L3 for workflow)
- [ ] Operation type is compatible (READ/WRITE/TRANSFORM)
- [ ] Input schema can be satisfied
- [ ] Output schema provides what you need
- [ ] Tool requirements are available in your environment
- [ ] Approval requirements align with your process
- [ ] Error handling covers your scenarios
