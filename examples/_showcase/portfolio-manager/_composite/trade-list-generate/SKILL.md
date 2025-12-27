# trade-list-generate

Generate concrete trade list to move from current to target allocation.

```yaml
name: trade-list-generate
version: 1.0.0
level: 2
category: portfolio-construction
operation: READ

description: >
  Create a specific trade list (buy/sell amounts) to transition
  from current portfolio to target allocation. Optimises for
  minimal cost, tax efficiency, and constraint compliance.

composes:
  - portfolio-summarise
  - market-data-fetch
  - constraint-validate
  - tax-impact-estimate

requires_approval: false  # Only generates list, doesn't execute
```

## Input Schema

```yaml
input:
  current_portfolio:
    type: object
    description: Current holdings with cost basis

  target_allocation:
    type: object
    description: Desired end-state allocation
    properties:
      by_asset_class:
        type: object
      by_security:
        type: array
        items:
          security_id: string
          target_weight: number

  constraints:
    type: object
    properties:
      min_trade_size:
        type: number
        default: 500
        description: Minimum trade value
      max_trades:
        type: number
        description: Maximum number of trades
      exclude_securities:
        type: array
        description: Don't trade these
      lot_selection:
        type: enum
        values: [fifo, lifo, hifo, specific, tax_optimal]
        default: tax_optimal
      wash_sale_check:
        type: boolean
        default: true

  optimisation_goals:
    type: array
    default: [minimise_trades, minimise_tax, minimise_cost]
    items:
      type: enum
      values:
        - minimise_trades     # Fewest trades
        - minimise_tax        # Lowest tax impact
        - minimise_cost       # Lowest commission
        - minimise_tracking   # Closest to target
        - avoid_short_term    # Prefer long-term gains

  execution_preferences:
    type: object
    properties:
      urgency: enum [immediate, opportunistic, patient]
      order_type: enum [market, limit]
      limit_buffer_pct: number  # % below/above market for limits
```

## Output Schema

```yaml
output:
  trade_list:
    type: array
    items:
      sequence: number
      action: enum [buy, sell]
      security_id: string
      security_name: string
      quantity: number
      estimated_price: number
      estimated_value: number
      lot_details:
        type: array
        items:
          lot_id: string
          quantity: number
          cost_basis: number
          acquisition_date: date
          holding_period: enum [short_term, long_term]
          gain_loss: number
      order_type: string
      limit_price: number  # If applicable
      rationale: string

  summary:
    total_buys: number
    total_sells: number
    net_cashflow: number
    estimated_commission: number
    trades_count: number

  tax_impact:
    total_realised_gains: number
    short_term_gains: number
    long_term_gains: number
    losses_harvested: number
    net_tax_liability: number
    tax_rate_assumed: number

  allocation_result:
    before:
      type: object
    after:
      type: object
    tracking_error_vs_target: number

  constraint_check:
    all_passed: boolean
    violations: array
    warnings: array

  alternatives:
    type: array
    description: Alternative trade sets considered
    items:
      name: string
      trades_count: number
      tax_impact: number
      tracking_error: number
      reason_not_selected: string

  execution_plan:
    recommended_sequence: array
    timing_notes: string
    market_impact_warning: boolean
```

## Optimisation Logic

```yaml
optimisation_algorithm:
  step_1_calculate_deltas:
    description: |
      For each security, calculate:
      - Current weight vs target weight
      - Dollar amount to buy or sell
      - Filter out changes below min_trade_size

  step_2_lot_selection:
    description: |
      For sells, select lots based on preference:
      - tax_optimal: Minimise tax (losses first, then long-term gains)
      - fifo: First in, first out
      - hifo: Highest cost first (minimise gains)
      - specific: User-specified lots

  step_3_apply_constraints:
    description: |
      Check each trade against:
      - Position limits
      - Sector/concentration limits
      - Excluded securities
      - Wash sale rules

  step_4_optimise:
    description: |
      Based on optimisation_goals:
      - minimise_trades: Combine small trades, widen bands
      - minimise_tax: Prioritise loss harvesting, defer gains
      - minimise_tracking: Accept more trades for precision

  step_5_sequence:
    description: |
      Order trades for execution:
      - Sells before buys (generate cash)
      - Larger trades first
      - Related trades together
```

## Tax Optimisation Strategies

```yaml
tax_strategies:
  loss_harvesting:
    description: "Realise losses to offset gains"
    trigger: unrealised_loss > threshold
    action: "Sell losing position, replace with similar"
    wash_sale_check: true

  gain_deferral:
    description: "Delay realising gains when possible"
    approach: |
      - Prefer selling lots with smaller gains
      - Wait for long-term holding period if close
      - Use alternatives to achieve allocation

  long_term_preference:
    description: "Favour long-term gains (lower tax rate)"
    approach: |
      - If selling, prefer lots held > 12 months
      - Flag short-term sales for review

  cgt_discount:
    jurisdiction: australia
    description: "50% CGT discount for assets held > 12 months"
    action: "Highlight if sale would miss discount by < 30 days"
```

## Example Output

```yaml
output:
  trade_list:
    - sequence: 1
      action: sell
      security_id: "CBA.AX"
      security_name: "Commonwealth Bank"
      quantity: 50
      estimated_price: 142.50
      estimated_value: 7125.00
      lot_details:
        - lot_id: "LOT-001"
          quantity: 50
          cost_basis: 5250.00
          acquisition_date: "2022-03-15"
          holding_period: "long_term"
          gain_loss: 1875.00
      order_type: "limit"
      limit_price: 142.00
      rationale: "Reduce overweight Financials, realise long-term gain"

    - sequence: 2
      action: buy
      security_id: "VGS.AX"
      security_name: "Vanguard MSCI Intl"
      quantity: 75
      estimated_price: 95.20
      estimated_value: 7140.00
      order_type: "limit"
      limit_price: 95.50
      rationale: "Increase international equity to target weight"

  summary:
    total_buys: 7140.00
    total_sells: 7125.00
    net_cashflow: -15.00
    estimated_commission: 19.90
    trades_count: 2

  tax_impact:
    total_realised_gains: 1875.00
    short_term_gains: 0
    long_term_gains: 1875.00
    losses_harvested: 0
    net_tax_liability: 398.44  # At 42.5% marginal, 50% discount
    tax_rate_assumed: 0.425

  allocation_result:
    before:
      financials: 25.0
      international_equity: 28.0
    after:
      financials: 23.5
      international_equity: 29.5
    tracking_error_vs_target: 0.8

  constraint_check:
    all_passed: true
    violations: []
    warnings:
      - "Financials still 1.5% above target (within tolerance)"

  execution_plan:
    recommended_sequence:
      - "1. Sell CBA.AX (generates cash)"
      - "2. Buy VGS.AX (uses proceeds)"
    timing_notes: "Execute on same day to minimise cash drag"
    market_impact_warning: false
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Target unachievable | Show closest possible, explain gap |
| Wash sale conflict | Defer trade, suggest alternative |
| Insufficient cash for buys | Sequence sells first or reduce buys |
| Constraint violation | Adjust trades, flag for override |
