# constraint-validate

Validate proposed actions against Investment Policy Statement constraints.

```yaml
name: constraint-validate
version: 1.0.0
level: 1
category: policy-controls
operation: READ

description: >
  Check whether a proposed portfolio state or trade list complies
  with defined constraints (IPS rules, regulatory limits, internal
  policies). Returns pass/fail with detailed violation report.

tools:
  preferred:
    - name: rules_engine
      operations: [evaluate]
  fallback:
    - name: internal
      description: Built-in constraint evaluation
```

## Input Schema

```yaml
input:
  portfolio_state:
    type: object
    description: Current or proposed portfolio state
    properties:
      holdings:
        type: array
        items:
          security_id: string
          weight: number
          value: number
          asset_class: string
          sector: string
          country: string
      total_value: number
      cash_balance: number

  proposed_trades:
    type: array
    description: Optional - trades to validate
    items:
      security_id: string
      action: enum [buy, sell]
      quantity: number
      estimated_value: number

  constraints:
    type: object
    description: Rules to check against (or reference to IPS)
    properties:
      ips_reference:
        type: string
        description: Reference to stored IPS document

      max_position_weight:
        type: number
        description: Maximum single position as % of portfolio

      max_sector_weight:
        type: number
        description: Maximum sector allocation %

      max_country_weight:
        type: number
        description: Maximum single country allocation %

      min_cash_buffer:
        type: number
        description: Minimum cash as % of portfolio

      excluded_sectors:
        type: array
        description: Sectors not allowed (ESG/ethical)

      excluded_securities:
        type: array
        description: Specific securities not allowed

      allowed_asset_classes:
        type: array
        description: Permitted asset classes

      max_leverage:
        type: number
        default: 1.0
        description: Maximum leverage ratio (1.0 = no leverage)

      liquidity_requirement:
        type: number
        description: % that must be liquid within X days
```

## Output Schema

```yaml
output:
  valid:
    type: boolean
    description: True if all constraints pass

  violations:
    type: array
    items:
      constraint:
        type: string
        description: Name of violated constraint
      severity:
        type: enum
        values: [hard, soft]
        description: Hard = must fix, Soft = warning
      current_value:
        type: number
        description: Actual value
      limit:
        type: number
        description: Constraint limit
      breach_amount:
        type: number
        description: How much over/under limit
      affected_holdings:
        type: array
        description: Securities involved in breach
      remediation:
        type: string
        description: Suggested fix

  warnings:
    type: array
    description: Near-breach situations (within 10% of limit)

  summary:
    type: object
    properties:
      total_checks: number
      passed: number
      failed_hard: number
      failed_soft: number
      warnings: number
```

## Constraint Types

### Position Limits
```yaml
position_limits:
  single_security_max: 10%    # No position > 10%
  top_5_max: 40%              # Top 5 positions < 40%
  single_issuer_max: 15%      # Including bonds from same issuer
```

### Sector/Industry Limits
```yaml
sector_limits:
  max_any_sector: 30%
  specific:
    financials: 25%
    technology: 25%
    energy: 15%
```

### Geographic Limits
```yaml
geographic_limits:
  domestic_min: 40%           # Home bias requirement
  single_country_max: 50%
  emerging_markets_max: 20%
```

### Asset Class Limits
```yaml
asset_class_limits:
  equities: { min: 40%, max: 80% }
  fixed_income: { min: 10%, max: 40% }
  alternatives: { max: 15% }
  cash: { min: 2%, max: 20% }
```

### ESG/Exclusion Rules
```yaml
exclusions:
  sectors:
    - tobacco
    - gambling
    - weapons_controversial
    - thermal_coal

  specific_securities:
    - "AU000XYZ123"  # Specific exclusion

  screens:
    - ungc_violators          # UN Global Compact
    - controversial_weapons
    - thermal_coal_revenue_5pct
```

## Example Usage

```yaml
# Check proposed portfolio state
input:
  portfolio_state:
    holdings:
      - security_id: "CBA.AX"
        weight: 12.5
        sector: "Financials"
      - security_id: "BHP.AX"
        weight: 11.0
        sector: "Materials"
      - security_id: "WOW.AX"
        weight: 8.0
        sector: "Consumer Staples"
    total_value: 500000
    cash_balance: 10000

  constraints:
    max_position_weight: 10
    max_sector_weight: 25
    min_cash_buffer: 2

# Output
output:
  valid: false
  violations:
    - constraint: "max_position_weight"
      severity: "hard"
      current_value: 12.5
      limit: 10
      breach_amount: 2.5
      affected_holdings: ["CBA.AX"]
      remediation: "Reduce CBA.AX by $12,500 to bring to 10% weight"
    - constraint: "max_position_weight"
      severity: "hard"
      current_value: 11.0
      limit: 10
      breach_amount: 1.0
      affected_holdings: ["BHP.AX"]
      remediation: "Reduce BHP.AX by $5,000 to bring to 10% weight"
  warnings:
    - constraint: "min_cash_buffer"
      current_value: 2.0
      limit: 2.0
      message: "Cash at minimum threshold"
  summary:
    total_checks: 5
    passed: 3
    failed_hard: 2
    failed_soft: 0
    warnings: 1
```

## Severity Levels

| Severity | Action | Examples |
|----------|--------|----------|
| **Hard** | Must resolve before proceeding | Excluded security, leverage limit |
| **Soft** | Warning, can override with justification | Near concentration limit |
| **Info** | Informational only | Approaching threshold |

## Error Handling

| Error | Recovery |
|-------|----------|
| Missing constraint definition | Use defaults, warn |
| Unknown security classification | Flag for manual review |
| Circular constraint reference | Detect and report |
| Conflicting constraints | Report impossibility |
