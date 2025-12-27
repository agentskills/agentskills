# drift-monitor

Monitor portfolio for drift, concentration breaches, and loss thresholds.

```yaml
name: drift-monitor
version: 1.0.0
level: 2
category: monitoring
operation: READ

description: >
  Continuously monitor portfolio against defined thresholds.
  Alerts when asset weights drift, concentration limits breach,
  or losses exceed acceptable levels.

composes:
  - portfolio-summarise
  - market-data-fetch
  - alert-send
```

## Input Schema

```yaml
input:
  portfolio:
    type: object

  target_allocation:
    type: object
    description: Target weights to monitor against

  thresholds:
    type: object
    properties:
      # Drift thresholds
      absolute_drift:
        type: number
        default: 5
        description: Alert if any asset class drifts > X% from target

      relative_drift:
        type: number
        default: 25
        description: Alert if drift > X% of target (e.g., 5% target, 25% relative = 1.25%)

      # Concentration thresholds
      single_position_max:
        type: number
        default: 10
        description: Alert if any position exceeds X%

      sector_max:
        type: number
        default: 30
        description: Alert if any sector exceeds X%

      top_5_max:
        type: number
        default: 50
        description: Alert if top 5 positions exceed X%

      # Loss thresholds
      daily_loss:
        type: number
        default: 3
        description: Alert if daily loss exceeds X%

      weekly_loss:
        type: number
        default: 5

      monthly_loss:
        type: number
        default: 10

      peak_drawdown:
        type: number
        default: 15
        description: Alert if drawdown from peak exceeds X%

      # Liquidity thresholds
      cash_minimum:
        type: number
        default: 2
        description: Alert if cash falls below X%

  monitoring_frequency:
    type: enum
    values: [realtime, hourly, daily, weekly]
    default: daily

  alert_channels:
    type: array
    default: [email]
```

## Output Schema

```yaml
output:
  monitoring_timestamp:
    type: datetime

  status:
    overall: enum [green, amber, red]
    message: string

  drift_status:
    type: array
    items:
      category: string
      target_weight: number
      current_weight: number
      drift_absolute: number
      drift_relative: number
      status: enum [ok, warning, breach]
      recommendation: string

  concentration_status:
    single_position:
      status: enum [ok, warning, breach]
      breaches: array
    sector:
      status: enum [ok, warning, breach]
      breaches: array
    top_5:
      current: number
      limit: number
      status: enum [ok, warning, breach]

  loss_status:
    daily:
      return: number
      threshold: number
      status: enum [ok, breach]
    weekly:
      return: number
      threshold: number
      status: enum [ok, breach]
    monthly:
      return: number
      threshold: number
      status: enum [ok, breach]
    peak_drawdown:
      current: number
      threshold: number
      peak_date: date
      status: enum [ok, warning, breach]

  liquidity_status:
    cash_percentage: number
    minimum_required: number
    status: enum [ok, warning, breach]

  alerts_triggered:
    type: array
    items:
      alert_type: string
      severity: enum [info, warning, critical]
      message: string
      data: object
      sent_to: array

  rebalance_recommendation:
    needed: boolean
    urgency: enum [none, low, medium, high]
    reason: string
    estimated_trades: number
```

## Threshold Escalation

```yaml
escalation_levels:
  # Drift
  drift:
    ok: "< 50% of threshold"
    warning: "50-100% of threshold"
    breach: "> 100% of threshold"

  # Concentration
  concentration:
    ok: "< 80% of limit"
    warning: "80-100% of limit"
    breach: "> 100% of limit"

  # Loss
  loss:
    ok: "No threshold breached"
    warning: "Within 20% of threshold"
    breach: "Threshold exceeded"

alert_rules:
  - condition: "breach"
    action: "Immediate alert via all channels"
    include_recommendation: true

  - condition: "warning"
    action: "Daily digest only"
    include_recommendation: false

  - condition: "multiple_warnings"
    threshold: 3
    action: "Escalate to immediate alert"
```

## Example Output

```yaml
output:
  monitoring_timestamp: "2024-12-20T16:00:00+11:00"

  status:
    overall: "amber"
    message: "2 drift warnings, 1 concentration warning"

  drift_status:
    - category: "Australian Equities"
      target_weight: 40.0
      current_weight: 44.5
      drift_absolute: 4.5
      drift_relative: 11.25
      status: "warning"
      recommendation: "Approaching rebalance threshold"

    - category: "International Equities"
      target_weight: 30.0
      current_weight: 26.2
      drift_absolute: -3.8
      drift_relative: -12.67
      status: "warning"
      recommendation: "Consider topping up on next contribution"

    - category: "Fixed Income"
      target_weight: 20.0
      current_weight: 19.8
      drift_absolute: -0.2
      drift_relative: -1.0
      status: "ok"

    - category: "Cash"
      target_weight: 10.0
      current_weight: 9.5
      drift_absolute: -0.5
      drift_relative: -5.0
      status: "ok"

  concentration_status:
    single_position:
      status: "warning"
      breaches:
        - security: "CBA.AX"
          current_weight: 9.2
          limit: 10.0
          headroom: 0.8
    sector:
      status: "ok"
      breaches: []
    top_5:
      current: 42.0
      limit: 50.0
      status: "ok"

  loss_status:
    daily:
      return: -0.8
      threshold: -3.0
      status: "ok"
    weekly:
      return: -2.1
      threshold: -5.0
      status: "ok"
    monthly:
      return: 1.5
      threshold: -10.0
      status: "ok"
    peak_drawdown:
      current: -5.2
      threshold: -15.0
      peak_date: "2024-11-28"
      status: "ok"

  liquidity_status:
    cash_percentage: 9.5
    minimum_required: 2.0
    status: "ok"

  alerts_triggered:
    - alert_type: "drift_warning"
      severity: "warning"
      message: "Australian Equities at 44.5%, target 40%"
      data:
        category: "Australian Equities"
        drift: 4.5
      sent_to: []  # Suppressed (warning level)

  rebalance_recommendation:
    needed: false
    urgency: "low"
    reason: "Drift within tolerance but approaching threshold"
    estimated_trades: 2
```

## Monitoring Modes

```yaml
modes:
  passive:
    description: "Monitor and report only"
    auto_alert: true
    auto_rebalance: false

  semi_active:
    description: "Monitor, alert, and propose rebalance"
    auto_alert: true
    auto_rebalance: false
    generate_trade_list: true

  active:
    description: "Monitor and auto-rebalance within bands"
    auto_alert: true
    auto_rebalance: true
    requires_approval: true  # Still needs human approval
    rebalance_threshold: "breach"
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Market data delayed | Use last known, flag staleness |
| Target allocation missing | Use last known or default |
| Alert delivery fails | Queue and retry |
| Calculation error | Log, alert ops, use fallback |
