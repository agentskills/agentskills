# risk-profile-estimate

Estimate portfolio's risk profile including volatility, drawdown, and factor exposures.

```yaml
name: risk-profile-estimate
version: 1.0.0
level: 2
category: portfolio-understanding
operation: READ

description: >
  Comprehensive risk assessment of portfolio including volatility,
  drawdown characteristics, concentration risk, and factor exposures.
  Translates technical metrics into investor-relevant risk context.

composes:
  - holdings-ingest
  - market-data-fetch
  - risk-metrics-calculate

tools:
  preferred:
    - name: risk_analytics
      operations: [factor_analysis, stress_test]
```

## Input Schema

```yaml
input:
  portfolio:
    type: object
    description: Portfolio to analyse (or reference)

  analysis_depth:
    type: enum
    values: [basic, standard, comprehensive]
    default: standard

  lookback_years:
    type: number
    default: 3
    description: Historical period for analysis

  factor_model:
    type: enum
    values: [none, fama_french_3, fama_french_5, barra, custom]
    default: fama_french_3

  peer_comparison:
    type: boolean
    default: false
    description: Compare to similar portfolios
```

## Output Schema

```yaml
output:
  risk_rating:
    score: number          # 1-10 scale
    category: string       # Conservative, Moderate, Aggressive, etc.
    description: string    # Plain English explanation

  volatility_profile:
    annualised_volatility: number
    volatility_percentile: number   # vs universe
    volatility_trend: string        # Increasing, Stable, Decreasing
    implied_range_1y:
      low: number
      high: number
      confidence: number

  drawdown_profile:
    max_drawdown_historical: number
    max_drawdown_date: string
    recovery_time_months: number
    current_drawdown: number
    expected_max_drawdown_1y: number  # Model-based

  concentration_risk:
    single_stock_risk:
      highest: string
      weight: number
      marginal_var_contribution: number
    sector_concentration:
      highest: string
      weight: number
    geographic_concentration:
      highest: string
      weight: number
    effective_positions: number

  factor_exposures:
    market_beta: number
    size: number          # SMB exposure
    value: number         # HML exposure
    momentum: number
    quality: number
    low_volatility: number
    interpretation: string  # Plain English

  tail_risk:
    var_95_1day: number
    var_99_1day: number
    cvar_95: number
    skewness: number
    kurtosis: number
    tail_risk_category: string  # Normal, Fat-tailed, etc.

  correlation_risk:
    average_pairwise_correlation: number
    correlation_to_benchmark: number
    diversification_benefit: number

  liquidity_risk:
    days_to_liquidate_95pct: number
    illiquid_holdings_pct: number
    liquidity_score: number

  stress_scenarios:
    type: array
    items:
      scenario: string
      portfolio_impact: number
      description: string

  risk_decomposition:
    systematic_risk_pct: number
    idiosyncratic_risk_pct: number
    top_risk_contributors:
      type: array
      items:
        security: string
        risk_contribution: number
```

## Risk Rating Scale

```yaml
risk_ratings:
  1-2:
    category: "Very Conservative"
    volatility_range: "0-5%"
    typical_drawdown: "0-5%"
    suitable_for: "Capital preservation, short horizon"

  3-4:
    category: "Conservative"
    volatility_range: "5-10%"
    typical_drawdown: "5-15%"
    suitable_for: "Income focus, moderate horizon"

  5-6:
    category: "Moderate"
    volatility_range: "10-15%"
    typical_drawdown: "15-25%"
    suitable_for: "Balanced growth/income, medium horizon"

  7-8:
    category: "Growth"
    volatility_range: "15-20%"
    typical_drawdown: "25-35%"
    suitable_for: "Capital growth, longer horizon"

  9-10:
    category: "Aggressive"
    volatility_range: "20%+"
    typical_drawdown: "35%+"
    suitable_for: "Maximum growth, long horizon, high tolerance"
```

## Stress Scenarios

```yaml
stress_tests:
  - name: "2008 GFC"
    description: "Global financial crisis replay"
    market_shock: -50%

  - name: "2020 COVID Crash"
    description: "Sharp pandemic-driven selloff"
    market_shock: -35%

  - name: "Rising Rates"
    description: "+200bp rate shock"
    bond_shock: -15%

  - name: "Stagflation"
    description: "High inflation + recession"
    equity_shock: -25%
    bond_shock: -10%

  - name: "AUD Crash"
    description: "20% AUD depreciation"
    fx_shock: -20%

  - name: "Sector Specific"
    description: "30% drop in largest sector"
    sector_shock: -30%
```

## Example Output

```yaml
output:
  risk_rating:
    score: 6.5
    category: "Moderate-Growth"
    description: |
      Your portfolio has moderate risk with growth orientation.
      Expect annual volatility around 13% and potential drawdowns
      of 20-25% in severe market conditions.

  volatility_profile:
    annualised_volatility: 13.2
    volatility_percentile: 55
    volatility_trend: "Stable"
    implied_range_1y:
      low: -18.0
      high: +22.0
      confidence: 0.95

  drawdown_profile:
    max_drawdown_historical: -22.5
    max_drawdown_date: "2022-06-16"
    recovery_time_months: 8
    current_drawdown: -3.2
    expected_max_drawdown_1y: -18.0

  factor_exposures:
    market_beta: 0.92
    size: 0.15
    value: -0.10
    momentum: 0.25
    quality: 0.30
    low_volatility: -0.05
    interpretation: |
      Slightly less sensitive to market than benchmark.
      Tilted toward momentum and quality stocks.
      Slight growth bias (negative value).

  stress_scenarios:
    - scenario: "2008 GFC"
      portfolio_impact: -38.5
      description: "Significant loss, less than market due to diversification"
    - scenario: "Rising Rates"
      portfolio_impact: -8.2
      description: "Moderate impact from fixed income allocation"

  risk_decomposition:
    systematic_risk_pct: 75
    idiosyncratic_risk_pct: 25
    top_risk_contributors:
      - security: "CBA.AX"
        risk_contribution: 18.5
      - security: "VGS.AX"
        risk_contribution: 15.2
```

## Composition Flow

```yaml
steps:
  1_gather_data:
    parallel:
      - skill: holdings-ingest
      - skill: market-data-fetch
        params:
          data_types: [price, history]

  2_calculate_metrics:
    skill: risk-metrics-calculate
    input:
      portfolio: ${holdings}
      returns_history: ${market_data.history}

  3_factor_analysis:
    action: internal
    description: Run factor model regression

  4_stress_test:
    action: internal
    description: Apply stress scenarios

  5_synthesise:
    action: internal
    description: |
      Combine all metrics into risk rating
      Generate plain English interpretation
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Insufficient history | Use available data, flag reliability |
| Factor model failure | Fall back to simpler model |
| Stress scenario undefined | Use generic market shock |
