# whatif-simulate

Run what-if simulations for portfolio changes.

```yaml
name: whatif-simulate
version: 1.0.0
level: 2
category: monitoring
operation: READ

description: >
  Simulate the impact of adding, removing, or changing positions
  before execution. Shows effect on risk, return, diversification,
  and constraint compliance.

composes:
  - portfolio-summarise
  - risk-metrics-calculate
  - constraint-validate
```

## Input Schema

```yaml
input:
  current_portfolio:
    type: object

  simulations:
    type: array
    items:
      name:
        type: string
        description: Simulation label
      changes:
        type: array
        items:
          action: enum [add, remove, increase, decrease, replace]
          security_id: string
          amount: number  # Value or weight depending on context
          amount_type: enum [value, weight, quantity]
          replace_with: string  # For replace action

  compare_to:
    type: array
    description: Benchmarks or alternatives to compare against
    items:
      type: string

  metrics_to_calculate:
    type: array
    default: [risk, return, diversification, constraints, income]
```

## Output Schema

```yaml
output:
  simulations:
    type: array
    items:
      name: string
      changes_summary: string

      resulting_portfolio:
        holdings: array
        total_value: number

      impact:
        risk:
          volatility_before: number
          volatility_after: number
          volatility_change: number
          var_95_before: number
          var_95_after: number
          max_drawdown_expected_change: number

        return:
          expected_return_before: number
          expected_return_after: number
          return_change: number
          yield_before: number
          yield_after: number

        diversification:
          effective_positions_before: number
          effective_positions_after: number
          correlation_change: number
          concentration_change: string

        constraints:
          violations_before: array
          violations_after: array
          new_violations: array
          resolved_violations: array

        costs:
          transaction_cost: number
          tax_impact: number
          ongoing_cost_change: number

      recommendation:
        verdict: enum [beneficial, neutral, detrimental]
        confidence: number
        key_considerations: array

  comparison_matrix:
    type: object
    description: Side-by-side comparison of all simulations
    properties:
      scenarios: array
      metrics: array
      values: object

  best_option:
    name: string
    reason: string
```

## Simulation Types

```yaml
simulation_types:
  add_position:
    description: "Add a new holding to portfolio"
    required: [security_id, amount]
    example:
      action: add
      security_id: "NDQ.AX"
      amount: 10000
      amount_type: value

  remove_position:
    description: "Sell entire position"
    required: [security_id]
    example:
      action: remove
      security_id: "CBA.AX"

  adjust_weight:
    description: "Change position size"
    required: [security_id, amount]
    example:
      action: increase
      security_id: "VAS.AX"
      amount: 5
      amount_type: weight

  replace_position:
    description: "Swap one holding for another"
    required: [security_id, replace_with]
    example:
      action: replace
      security_id: "IOZ.AX"
      replace_with: "VAS.AX"

  rebalance_to_target:
    description: "Simulate rebalance to target"
    required: [target_allocation]
```

## Example Output

```yaml
output:
  simulations:
    - name: "Add NASDAQ ETF"
      changes_summary: "Add $10,000 to NDQ.AX (NASDAQ 100 ETF)"

      resulting_portfolio:
        holdings:
          # Updated holdings list
        total_value: 510000

      impact:
        risk:
          volatility_before: 13.2
          volatility_after: 14.1
          volatility_change: +0.9
          var_95_before: -2.1
          var_95_after: -2.3
          max_drawdown_expected_change: +2.5

        return:
          expected_return_before: 7.5
          expected_return_after: 8.2
          return_change: +0.7
          yield_before: 3.2
          yield_after: 3.0

        diversification:
          effective_positions_before: 8.3
          effective_positions_after: 8.8
          correlation_change: "Slight increase due to tech overlap"
          concentration_change: "Technology exposure +5%"

        constraints:
          violations_before: []
          violations_after: []
          new_violations: []
          resolved_violations: []

        costs:
          transaction_cost: 9.95
          tax_impact: 0
          ongoing_cost_change: +15  # Higher MER

      recommendation:
        verdict: "beneficial"
        confidence: 0.72
        key_considerations:
          - "Increases expected return by 0.7%"
          - "Modest increase in volatility (+0.9%)"
          - "Adds tech sector concentration"
          - "No constraint violations"

    - name: "Replace CBA with VAS"
      changes_summary: "Sell CBA.AX, buy equivalent VAS.AX"

      impact:
        risk:
          volatility_before: 13.2
          volatility_after: 12.8
          volatility_change: -0.4

        diversification:
          effective_positions_before: 8.3
          effective_positions_after: 9.1
          concentration_change: "Reduces single-stock risk"

        costs:
          transaction_cost: 19.90
          tax_impact: 398.44  # CGT on CBA gain
          ongoing_cost_change: -25  # Lower cost via ETF

      recommendation:
        verdict: "beneficial"
        confidence: 0.85
        key_considerations:
          - "Improves diversification (single stock to index)"
          - "Reduces volatility slightly"
          - "One-time tax cost of $398"
          - "Lower ongoing costs"

  comparison_matrix:
    scenarios: ["Current", "Add NDQ", "Replace CBA→VAS"]
    metrics: ["Volatility", "Expected Return", "Yield", "Eff. Positions"]
    values:
      volatility: [13.2, 14.1, 12.8]
      expected_return: [7.5, 8.2, 7.3]
      yield: [3.2, 3.0, 3.4]
      effective_positions: [8.3, 8.8, 9.1]

  best_option:
    name: "Replace CBA with VAS"
    reason: "Best risk-adjusted improvement with better diversification"
```

## Analysis Dimensions

```yaml
analysis_dimensions:
  risk:
    - volatility
    - var_95
    - expected_max_drawdown
    - beta
    - tail_risk

  return:
    - expected_return
    - dividend_yield
    - total_return_estimate

  diversification:
    - effective_positions
    - sector_concentration
    - geographic_concentration
    - factor_exposures

  constraints:
    - ips_compliance
    - concentration_limits
    - excluded_securities

  costs:
    - transaction_costs
    - tax_implications
    - ongoing_fees
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Unknown security | Suggest alternatives, skip |
| Invalid amount | Validate, return error |
| Conflicting changes | Process in order, warn |
| Missing market data | Use estimates, flag |
