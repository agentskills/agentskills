# scenario-analyse

Analyse portfolio behaviour under different market scenarios.

```yaml
name: scenario-analyse
version: 1.0.0
level: 2
category: portfolio-understanding
operation: READ

description: >
  Project portfolio performance under various market conditions
  including rate changes, recessions, inflation shocks, and
  custom scenarios. Helps investors understand potential outcomes.

composes:
  - portfolio-summarise
  - risk-metrics-calculate
  - market-data-fetch

tools:
  preferred:
    - name: scenario_engine
      operations: [run_scenario, monte_carlo]
```

## Input Schema

```yaml
input:
  portfolio:
    type: object
    description: Portfolio to analyse

  scenarios:
    type: array
    items:
      type: enum
      values:
        - rate_hike_100bp
        - rate_hike_200bp
        - rate_cut_100bp
        - recession_mild
        - recession_severe
        - inflation_spike
        - deflation
        - equity_bull
        - equity_bear
        - credit_crisis
        - currency_crisis_aud
        - stagflation
        - tech_crash
        - gfc_replay
        - covid_crash
        - custom
    default: [rate_hike_100bp, recession_mild, equity_bear]

  custom_scenarios:
    type: array
    description: User-defined scenarios
    items:
      name: string
      shocks:
        equity: number
        fixed_income: number
        credit_spreads: number
        rates: number
        fx_aud: number
        commodities: number
        volatility: number

  time_horizon:
    type: string
    default: "1Y"
    description: Projection period

  monte_carlo:
    type: object
    description: Optional Monte Carlo simulation
    properties:
      enabled: boolean
      simulations: number
      confidence_levels: array
```

## Output Schema

```yaml
output:
  base_case:
    expected_return: number
    expected_volatility: number
    range_95: object

  scenario_results:
    type: array
    items:
      scenario: string
      description: string
      probability_estimate: number
      portfolio_impact:
        return: number
        value_change: number
      component_impacts:
        type: array
        items:
          asset_class: string
          weight: number
          impact: number
          contribution: number
      key_drivers: array
      hedging_suggestions: array

  comparative_analysis:
    best_case_scenario: string
    worst_case_scenario: string
    most_likely_scenario: string
    scenario_range:
      min_return: number
      max_return: number

  monte_carlo_results:
    median_return: number
    percentile_5: number
    percentile_25: number
    percentile_75: number
    percentile_95: number
    probability_of_loss: number
    var_95: number
    distribution_chart_data: array

  recommendations:
    type: array
    items:
      scenario: string
      action: string
      rationale: string
```

## Pre-Built Scenarios

```yaml
scenarios:
  rate_hike_100bp:
    name: "Interest Rate Rise (+1%)"
    description: "Central bank raises rates by 100 basis points"
    shocks:
      rates: +1.0
      equity: -5.0
      fixed_income: -8.0
      growth_stocks: -10.0
      value_stocks: -2.0
      reits: -12.0

  rate_hike_200bp:
    name: "Aggressive Rate Rise (+2%)"
    description: "Rapid tightening cycle"
    shocks:
      rates: +2.0
      equity: -12.0
      fixed_income: -15.0
      credit_spreads: +50

  recession_mild:
    name: "Mild Recession"
    description: "GDP contracts 1-2%, elevated unemployment"
    shocks:
      equity: -20.0
      credit_spreads: +100
      rates: -0.5
      commodities: -15.0

  recession_severe:
    name: "Severe Recession"
    description: "GDP contracts 4%+, credit stress"
    shocks:
      equity: -40.0
      credit_spreads: +300
      high_yield: -25.0
      rates: -1.0

  inflation_spike:
    name: "Inflation Surge"
    description: "Inflation rises to 8%+"
    shocks:
      rates: +1.5
      tips: +5.0
      equity: -10.0
      fixed_income: -12.0
      commodities: +20.0
      gold: +15.0

  stagflation:
    name: "Stagflation"
    description: "High inflation + economic stagnation"
    shocks:
      equity: -25.0
      fixed_income: -10.0
      commodities: +15.0
      rates: +0.5

  equity_bear:
    name: "Equity Bear Market"
    description: "20%+ decline in equity markets"
    shocks:
      equity: -25.0
      volatility: +80.0
      credit_spreads: +75
      gold: +10.0

  gfc_replay:
    name: "GFC-Style Crisis"
    description: "2008-style financial crisis"
    shocks:
      equity: -50.0
      credit_spreads: +400
      high_yield: -35.0
      volatility: +200.0
      rates: -2.0

  covid_crash:
    name: "Pandemic Shock"
    description: "Rapid market selloff like March 2020"
    shocks:
      equity: -35.0
      volatility: +150.0
      credit_spreads: +200
      oil: -60.0
```

## Example Output

```yaml
output:
  base_case:
    expected_return: 7.5
    expected_volatility: 13.2
    range_95:
      low: -18.0
      high: +33.0

  scenario_results:
    - scenario: "rate_hike_100bp"
      description: "Central bank raises rates by 100 basis points"
      probability_estimate: 0.25
      portfolio_impact:
        return: -6.8
        value_change: -34000
      component_impacts:
        - asset_class: "Australian Equities"
          weight: 40.0
          impact: -5.0
          contribution: -2.0
        - asset_class: "Fixed Income"
          weight: 20.0
          impact: -8.0
          contribution: -1.6
        - asset_class: "International Equities"
          weight: 30.0
          impact: -7.0
          contribution: -2.1
        - asset_class: "Cash"
          weight: 10.0
          impact: +1.0
          contribution: +0.1
      key_drivers:
        - "Fixed income duration exposure"
        - "Growth stock allocation"
      hedging_suggestions:
        - "Reduce duration in bond holdings"
        - "Increase value stock allocation"

    - scenario: "recession_mild"
      description: "GDP contracts 1-2%, elevated unemployment"
      probability_estimate: 0.15
      portfolio_impact:
        return: -15.2
        value_change: -76000
      # ...

  comparative_analysis:
    best_case_scenario: "equity_bull"
    worst_case_scenario: "gfc_replay"
    most_likely_scenario: "base_case"
    scenario_range:
      min_return: -42.0
      max_return: +28.0

  recommendations:
    - scenario: "rate_hike_100bp"
      action: "Consider reducing fixed income duration"
      rationale: "Portfolio has above-average sensitivity to rate rises"
    - scenario: "recession_mild"
      action: "Increase defensive sector allocation"
      rationale: "Cyclical exposure may amplify downturn impact"
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Missing asset class mapping | Use proxy, flag approximation |
| Scenario undefined | Use closest available scenario |
| Monte Carlo timeout | Reduce simulation count |
| Invalid custom scenario | Validate and return errors |
