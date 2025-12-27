# benchmark-compare

Compare portfolio against benchmark or model portfolio.

```yaml
name: benchmark-compare
version: 1.0.0
level: 2
category: portfolio-understanding
operation: READ

description: >
  Detailed comparison of portfolio against a benchmark index
  or model portfolio. Identifies key differences in allocation,
  risk, and performance attribution.

composes:
  - portfolio-summarise
  - market-data-fetch
  - risk-metrics-calculate
```

## Input Schema

```yaml
input:
  portfolio:
    type: object

  benchmark:
    type: string
    description: Benchmark identifier or "model_portfolio"
    examples:
      - "ASX200"
      - "MSCI_WORLD"
      - "60_40_BALANCED"
      - "model:conservative"
      - "model:growth"

  comparison_period:
    type: string
    default: "1Y"
    description: Period for performance comparison

  analysis_dimensions:
    type: array
    default: [allocation, performance, risk, style]
    items:
      type: enum
      values:
        - allocation
        - performance
        - risk
        - style
        - holdings
        - income
```

## Output Schema

```yaml
output:
  summary:
    portfolio_return: number
    benchmark_return: number
    excess_return: number
    tracking_error: number
    information_ratio: number
    verdict: string  # Outperformed, Underperformed, In-line

  allocation_comparison:
    by_asset_class:
      type: array
      items:
        asset_class: string
        portfolio_weight: number
        benchmark_weight: number
        active_weight: number
        contribution_to_tracking: number

    by_sector:
      type: array
      items:
        sector: string
        portfolio_weight: number
        benchmark_weight: number
        active_weight: number

    by_geography:
      type: array
      items:
        region: string
        portfolio_weight: number
        benchmark_weight: number
        active_weight: number

  performance_attribution:
    total_excess_return: number
    allocation_effect: number      # From different weights
    selection_effect: number       # From security selection
    interaction_effect: number     # Combined effect

    by_asset_class:
      type: array
      items:
        asset_class: string
        allocation_effect: number
        selection_effect: number
        total_effect: number

    top_contributors:
      type: array
      items:
        security: string
        contribution: number
        reason: string

    top_detractors:
      type: array
      items:
        security: string
        contribution: number
        reason: string

  risk_comparison:
    portfolio:
      volatility: number
      sharpe_ratio: number
      max_drawdown: number
      beta: number
    benchmark:
      volatility: number
      sharpe_ratio: number
      max_drawdown: number
    relative:
      tracking_error: number
      active_share: number
      r_squared: number

  style_comparison:
    portfolio_style:
      growth_value: number  # -100 to +100
      large_small: number   # -100 to +100
    benchmark_style:
      growth_value: number
      large_small: number
    style_drift: string

  holdings_overlap:
    overlap_percentage: number
    common_holdings: array
    portfolio_only: array
    benchmark_only: array

  key_differences:
    type: array
    items:
      category: string
      observation: string
      impact: string
      recommendation: string
```

## Benchmark Definitions

```yaml
benchmarks:
  # Index benchmarks
  ASX200:
    name: "S&P/ASX 200"
    type: index
    asset_class: australian_equity

  MSCI_WORLD:
    name: "MSCI World"
    type: index
    asset_class: international_equity

  AUSBOND:
    name: "Bloomberg AusBond Composite"
    type: index
    asset_class: fixed_income

  # Model portfolios
  60_40_BALANCED:
    name: "60/40 Balanced"
    type: model
    allocation:
      australian_equity: 24
      international_equity: 36
      fixed_income: 32
      cash: 8

  model_conservative:
    name: "Conservative Model"
    type: model
    allocation:
      australian_equity: 15
      international_equity: 15
      fixed_income: 50
      cash: 20

  model_growth:
    name: "Growth Model"
    type: model
    allocation:
      australian_equity: 35
      international_equity: 45
      fixed_income: 15
      cash: 5
```

## Example Output

```yaml
output:
  summary:
    portfolio_return: 9.5
    benchmark_return: 8.2
    excess_return: 1.3
    tracking_error: 3.2
    information_ratio: 0.41
    verdict: "Outperformed benchmark by 1.3% with moderate tracking error"

  allocation_comparison:
    by_asset_class:
      - asset_class: "Australian Equities"
        portfolio_weight: 40.0
        benchmark_weight: 30.0
        active_weight: +10.0
        contribution_to_tracking: 0.8

      - asset_class: "International Equities"
        portfolio_weight: 30.0
        benchmark_weight: 40.0
        active_weight: -10.0
        contribution_to_tracking: 1.2

      - asset_class: "Fixed Income"
        portfolio_weight: 20.0
        benchmark_weight: 25.0
        active_weight: -5.0
        contribution_to_tracking: 0.4

  performance_attribution:
    total_excess_return: 1.3
    allocation_effect: 0.8
    selection_effect: 0.4
    interaction_effect: 0.1

    top_contributors:
      - security: "CBA.AX"
        contribution: 0.45
        reason: "Strong earnings beat, overweight position"
      - security: "CSL.AX"
        contribution: 0.32
        reason: "Healthcare sector rally"

    top_detractors:
      - security: "BHP.AX"
        contribution: -0.28
        reason: "Commodity price decline"

  risk_comparison:
    portfolio:
      volatility: 12.5
      sharpe_ratio: 0.68
      max_drawdown: -18.2
      beta: 0.92
    benchmark:
      volatility: 11.8
      sharpe_ratio: 0.62
      max_drawdown: -16.5
    relative:
      tracking_error: 3.2
      active_share: 42.0
      r_squared: 0.89

  key_differences:
    - category: "Asset Allocation"
      observation: "10% overweight Australian equities vs benchmark"
      impact: "Higher domestic exposure, reduced global diversification"
      recommendation: "Consider if home bias is intentional"

    - category: "Sector"
      observation: "5% overweight Financials"
      impact: "Concentration risk in rate-sensitive sector"
      recommendation: "Monitor given rate environment"
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Unknown benchmark | List available options |
| Missing benchmark data | Use closest proxy |
| Period mismatch | Align to common period |
| Holdings not in benchmark | Flag as active position |
