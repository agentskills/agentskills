# tax-impact-estimate

Estimate capital gains tax consequences of proposed trades.

```yaml
name: tax-impact-estimate
version: 1.0.0
level: 2
category: cashflow-tax
operation: READ

description: >
  Calculate the tax impact of proposed trades including capital
  gains, CGT discount eligibility, loss harvesting opportunities,
  and suggest tax-optimised alternatives.

composes:
  - holdings-ingest
  - market-data-fetch
```

## Input Schema

```yaml
input:
  proposed_trades:
    type: array
    required: true
    items:
      security_id: string
      action: enum [buy, sell]
      quantity: number
      lot_selection: enum [fifo, lifo, hifo, specific, tax_optimal]
      specific_lots: array  # If lot_selection = specific

  holdings_with_lots:
    type: object
    description: Current holdings with cost basis per lot

  tax_profile:
    type: object
    required: true
    properties:
      jurisdiction: enum [australia, us, uk, other]
      marginal_rate: number
      entity_type: enum [individual, trust, smsf, company]
      financial_year_end: date
      realised_gains_ytd: number
      realised_losses_ytd: number
      carried_forward_losses: number

  analysis_options:
    type: object
    properties:
      suggest_alternatives: boolean
      include_wash_sale_check: boolean
      include_timing_analysis: boolean
```

## Output Schema

```yaml
output:
  summary:
    gross_proceeds: number
    total_cost_basis: number
    total_gain_loss: number
    tax_liability: number
    effective_tax_rate: number
    net_proceeds: number

  by_trade:
    type: array
    items:
      security_id: string
      action: string
      quantity: number
      proceeds: number

      lot_analysis:
        type: array
        items:
          lot_id: string
          quantity: number
          cost_basis: number
          acquisition_date: date
          holding_period_days: number
          holding_period_type: enum [short_term, long_term]
          gain_loss: number
          taxable_gain: number  # After discount
          tax_impact: number

      total_gain_loss: number
      cgt_discount_applied: boolean
      discount_amount: number
      taxable_amount: number
      estimated_tax: number

  tax_breakdown:
    short_term_gains: number
    long_term_gains: number
    cgt_discount_benefit: number
    losses_realised: number
    net_taxable_gain: number

  offset_analysis:
    ytd_position:
      gains_before_trade: number
      losses_before_trade: number
      net_before_trade: number
    after_trade:
      total_gains: number
      total_losses: number
      net_position: number
    carried_losses_used: number
    carried_losses_remaining: number

  timing_analysis:
    holds_approaching_discount:
      type: array
      items:
        security_id: string
        lot_id: string
        acquisition_date: date
        discount_eligible_date: date
        days_until_eligible: number
        potential_tax_saving: number

  alternative_scenarios:
    type: array
    items:
      name: string
      description: string
      trades: array
      tax_impact: number
      savings_vs_proposed: number

  wash_sale_warnings:
    type: array
    items:
      security_id: string
      warning: string
      affected_amount: number

  recommendations:
    type: array
    items:
      priority: enum [high, medium, low]
      recommendation: string
      potential_saving: number
```

## Tax Rules by Jurisdiction

```yaml
tax_rules:
  australia:
    cgt_discount:
      threshold_days: 365
      discount_rate: 0.50
      applies_to: [individual, trust]
      not_for: [company, smsf]

    smsf_rates:
      accumulation: 0.15
      pension: 0.0

    loss_offset:
      capital_losses_offset: capital_gains_only
      carry_forward: indefinitely
      no_wash_sale_rule: true  # Australia doesn't have US-style wash sale

  us:
    long_term_threshold_days: 365
    rates:
      short_term: marginal_rate
      long_term:
        "0%": income < 44625
        "15%": income < 492300
        "20%": income >= 492300

    wash_sale:
      window_days: 30
      applies_to: losses
      disallowed_if: "repurchased substantially identical"

  uk:
    cgt_allowance_2024: 3000
    rates:
      basic_rate: 0.10
      higher_rate: 0.20
    bed_and_breakfast: 30  # Days before same-day matching
```

## Example Output

```yaml
output:
  summary:
    gross_proceeds: 25000
    total_cost_basis: 18500
    total_gain_loss: 6500
    tax_liability: 1381.25
    effective_tax_rate: 21.25
    net_proceeds: 23618.75

  by_trade:
    - security_id: "CBA.AX"
      action: "sell"
      quantity: 100
      proceeds: 14250

      lot_analysis:
        - lot_id: "LOT-001"
          quantity: 50
          cost_basis: 4500
          acquisition_date: "2022-03-15"
          holding_period_days: 1010
          holding_period_type: "long_term"
          gain_loss: 2625
          taxable_gain: 1312.50  # 50% discount
          tax_impact: 557.81

        - lot_id: "LOT-002"
          quantity: 50
          cost_basis: 5250
          acquisition_date: "2024-06-01"
          holding_period_days: 202
          holding_period_type: "short_term"
          gain_loss: 1875
          taxable_gain: 1875  # No discount
          tax_impact: 796.88

      total_gain_loss: 4500
      cgt_discount_applied: true
      discount_amount: 1312.50
      taxable_amount: 3187.50
      estimated_tax: 1354.69

    - security_id: "WOW.AX"
      action: "sell"
      quantity: 200
      proceeds: 10750

      lot_analysis:
        - lot_id: "LOT-003"
          quantity: 200
          cost_basis: 8750
          acquisition_date: "2023-01-10"
          holding_period_days: 710
          holding_period_type: "long_term"
          gain_loss: 2000
          taxable_gain: 1000  # 50% discount
          tax_impact: 425.00

      estimated_tax: 425.00

  tax_breakdown:
    short_term_gains: 1875
    long_term_gains: 4625
    cgt_discount_benefit: 2312.50
    losses_realised: 0
    net_taxable_gain: 4187.50

  timing_analysis:
    holds_approaching_discount:
      - security_id: "CBA.AX"
        lot_id: "LOT-002"
        acquisition_date: "2024-06-01"
        discount_eligible_date: "2025-06-01"
        days_until_eligible: 163
        potential_tax_saving: 398.44

  alternative_scenarios:
    - name: "Wait for CGT discount"
      description: "Delay CBA LOT-002 sale until June 2025"
      trades:
        - security_id: "CBA.AX"
          quantity: 50
          from_lot: "LOT-001"
      tax_impact: 955.25
      savings_vs_proposed: 425.94

    - name: "Harvest BHP loss first"
      description: "Sell BHP (unrealised loss) to offset CBA gains"
      trades:
        - security_id: "BHP.AX"
          action: "sell"
          gain_loss: -1500
        - security_id: "CBA.AX"
          action: "sell"
      tax_impact: 743.75
      savings_vs_proposed: 637.50

  recommendations:
    - priority: "high"
      recommendation: "Consider waiting 163 days for LOT-002 CGT discount"
      potential_saving: 398.44

    - priority: "medium"
      recommendation: "Harvest BHP loss before year end to offset gains"
      potential_saving: 637.50

    - priority: "low"
      recommendation: "Review timing of trades relative to financial year end"
      potential_saving: 0
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Missing cost basis | Prompt for input or use $0 |
| Unknown jurisdiction | Default to general rules, warn |
| Invalid lot selection | Fall back to FIFO |
| Rate uncertainty | Use conservative estimate |
