# risk-metrics-calculate

Calculate portfolio risk metrics including volatility, VaR, and drawdown.

```yaml
name: risk-metrics-calculate
version: 1.0.0
level: 1
category: portfolio-understanding
operation: READ

description: >
  Compute risk metrics for a portfolio or individual positions.
  Supports standard measures (volatility, VaR, Sharpe) and
  factor-based analysis.

tools:
  preferred:
    - name: quantlib
      operations: [calculate_risk]
    - name: risk_engine
      operations: [portfolio_risk, position_risk]
  fallback:
    - name: internal
      description: Built-in risk calculations using numpy/scipy
```

## Input Schema

```yaml
input:
  portfolio:
    type: object
    required: true
    properties:
      holdings:
        type: array
        items:
          security_id: string
          weight: number
          value: number
      total_value: number

  returns_history:
    type: object
    description: Historical returns (or will be fetched)
    properties:
      source: enum [provided, fetch]
      data:
        type: array
        items:
          date: date
          returns: object  # security_id -> return

  lookback_period:
    type: string
    default: "3Y"
    description: Period for historical analysis (1Y, 3Y, 5Y, 10Y)

  confidence_level:
    type: number
    default: 0.95
    description: Confidence level for VaR/CVaR (0.95 or 0.99)

  risk_free_rate:
    type: number
    default: 0.04
    description: Annual risk-free rate for Sharpe calculation

  benchmark:
    type: string
    description: Benchmark for beta/tracking error
```

## Output Schema

```yaml
output:
  as_of_date:
    type: date

  lookback_period:
    type: string

  # Volatility Measures
  volatility:
    annualised:
      type: number
      description: Annualised standard deviation of returns
    daily:
      type: number
    rolling_30d:
      type: number
    rolling_90d:
      type: number

  # Value at Risk
  var:
    historical:
      type: object
      properties:
        var_95: number
        var_99: number
        description: Percentile-based VaR
    parametric:
      type: object
      properties:
        var_95: number
        var_99: number
        description: Normal distribution VaR
    cvar_95:
      type: number
      description: Conditional VaR (Expected Shortfall)

  # Drawdown Analysis
  drawdown:
    current:
      type: number
      description: Current drawdown from peak
    max_drawdown:
      type: number
      description: Maximum drawdown in period
    max_drawdown_period:
      start_date: date
      end_date: date
      recovery_date: date
    average_drawdown:
      type: number

  # Risk-Adjusted Returns
  risk_adjusted:
    sharpe_ratio:
      type: number
      description: (Return - Rf) / Volatility
    sortino_ratio:
      type: number
      description: (Return - Rf) / Downside Deviation
    calmar_ratio:
      type: number
      description: Return / Max Drawdown
    information_ratio:
      type: number
      description: Active return / Tracking error

  # Relative Risk (if benchmark provided)
  relative:
    beta:
      type: number
      description: Sensitivity to benchmark
    alpha:
      type: number
      description: Risk-adjusted excess return
    tracking_error:
      type: number
      description: Volatility of excess returns
    r_squared:
      type: number
      description: Correlation with benchmark

  # Concentration Risk
  concentration:
    herfindahl_index:
      type: number
      description: Sum of squared weights (0-1)
    effective_positions:
      type: number
      description: 1 / HHI
    top_5_weight:
      type: number
    top_10_weight:
      type: number

  # Position-Level Risk
  position_risk:
    type: array
    items:
      security_id: string
      weight: number
      volatility: number
      var_contribution: number
      beta: number
      marginal_var: number
```

## Calculation Methods

### Volatility
```python
# Annualised volatility from daily returns
vol_annual = std(daily_returns) * sqrt(252)
```

### Value at Risk
```python
# Historical VaR (95%)
var_95 = percentile(returns, 5)

# Parametric VaR (assumes normal distribution)
var_95_param = mean(returns) - 1.645 * std(returns)

# CVaR (Expected Shortfall)
cvar_95 = mean(returns[returns <= var_95])
```

### Drawdown
```python
# Rolling maximum
rolling_max = cummax(portfolio_value)
drawdown = (portfolio_value - rolling_max) / rolling_max
max_drawdown = min(drawdown)
```

### Risk-Adjusted Ratios
```python
# Sharpe Ratio
sharpe = (annualised_return - risk_free_rate) / annualised_volatility

# Sortino Ratio (only downside deviation)
downside_returns = returns[returns < 0]
sortino = (annualised_return - risk_free_rate) / std(downside_returns) * sqrt(252)
```

## Example Usage

```yaml
input:
  portfolio:
    holdings:
      - security_id: "CBA.AX"
        weight: 0.20
        value: 100000
      - security_id: "BHP.AX"
        weight: 0.15
        value: 75000
      - security_id: "VAS.AX"
        weight: 0.40
        value: 200000
      - security_id: "VGS.AX"
        weight: 0.25
        value: 125000
    total_value: 500000
  lookback_period: "3Y"
  confidence_level: 0.95
  benchmark: "ASX200"

output:
  as_of_date: "2024-12-20"
  lookback_period: "3Y"

  volatility:
    annualised: 0.142
    daily: 0.0089
    rolling_30d: 0.128
    rolling_90d: 0.135

  var:
    historical:
      var_95: -0.021
      var_99: -0.032
    parametric:
      var_95: -0.019
      var_99: -0.029
    cvar_95: -0.028

  drawdown:
    current: -0.032
    max_drawdown: -0.185
    max_drawdown_period:
      start_date: "2022-01-05"
      end_date: "2022-06-16"
      recovery_date: "2023-02-28"
    average_drawdown: -0.045

  risk_adjusted:
    sharpe_ratio: 0.72
    sortino_ratio: 1.05
    calmar_ratio: 0.48
    information_ratio: 0.15

  relative:
    beta: 0.92
    alpha: 0.012
    tracking_error: 0.038
    r_squared: 0.87

  concentration:
    herfindahl_index: 0.265
    effective_positions: 3.77
    top_5_weight: 1.0
    top_10_weight: 1.0
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Insufficient history | Reduce lookback, warn on reliability |
| Missing returns data | Fetch via market-data-fetch |
| Singular covariance matrix | Use shrinkage estimator |
| Extreme outliers | Winsorise at 3 sigma, flag |
