# health-report-generate

Generate one-page portfolio health report for sharing.

```yaml
name: health-report-generate
version: 1.0.0
level: 2
category: explanation
operation: READ

description: >
  Create a concise, shareable portfolio health summary suitable
  for discussion with a human adviser, partner, or for personal
  records. Plain language with key metrics highlighted.

composes:
  - portfolio-summarise
  - risk-profile-estimate
  - benchmark-compare
  - suitability-assess
```

## Input Schema

```yaml
input:
  portfolio:
    type: object

  report_period:
    type: string
    default: "YTD"
    description: Period for performance reporting

  investor_profile:
    type: object
    description: For suitability commentary

  include_sections:
    type: array
    default: [summary, allocation, performance, risk, outlook, actions]

  format:
    type: enum
    values: [markdown, html, pdf]
    default: markdown

  audience:
    type: enum
    values: [self, adviser, partner, accountant]
    default: self
    description: Adjusts language and detail level
```

## Output Schema

```yaml
output:
  report:
    title: string
    generated_date: date
    report_period: string

    executive_summary:
      health_score: number  # 0-100
      health_status: string  # Excellent, Good, Needs Attention, Critical
      one_liner: string
      key_highlights:
        type: array
        items:
          type: string

    portfolio_snapshot:
      total_value: number
      total_value_formatted: string
      holdings_count: number
      last_updated: datetime

    allocation_overview:
      chart_data:
        type: array
        items:
          category: string
          weight: number
          target: number
          status: string
      narrative: string

    performance_summary:
      returns:
        mtd: number
        qtd: number
        ytd: number
        since_inception: number
        annualised: number
      vs_benchmark:
        benchmark_name: string
        benchmark_return: number
        relative_return: number
        verdict: string
      narrative: string

    risk_assessment:
      risk_score: number
      risk_category: string
      key_metrics:
        volatility: number
        max_drawdown: number
        sharpe_ratio: number
      concerns:
        type: array
      narrative: string

    goal_progress:
      type: array
      items:
        goal_name: string
        target: number
        current: number
        progress_pct: number
        on_track: boolean
        note: string

    suitability_check:
      aligned: boolean
      score: number
      notes: array

    action_items:
      type: array
      items:
        priority: enum [high, medium, low]
        action: string
        rationale: string
        deadline: string

    outlook:
      market_commentary: string
      portfolio_positioning: string
      recommendations: array

    appendix:
      holdings_table: array
      transaction_history: array
      fee_summary: object

  formatted_report:
    type: string
    description: Rendered report in requested format
```

## Report Sections

### Executive Summary
```yaml
executive_summary:
  health_score_calculation:
    components:
      - diversification: 25%
      - risk_alignment: 25%
      - performance: 20%
      - goal_progress: 20%
      - cost_efficiency: 10%

  health_status_thresholds:
    excellent: 85-100
    good: 70-84
    needs_attention: 50-69
    critical: 0-49
```

### Audience Adaptations
```yaml
audience_adaptations:
  self:
    detail_level: high
    jargon: allowed
    focus: comprehensive

  adviser:
    detail_level: high
    jargon: allowed
    focus: technical_metrics
    include: regulatory_notes

  partner:
    detail_level: medium
    jargon: minimal
    focus: goals_and_progress
    simplify: risk_metrics

  accountant:
    detail_level: high
    focus: tax_and_income
    include: cost_basis, dividends, CGT_events
```

## Example Output

```yaml
output:
  report:
    title: "Portfolio Health Report"
    generated_date: "2024-12-20"
    report_period: "Year to Date (2024)"

    executive_summary:
      health_score: 78
      health_status: "Good"
      one_liner: "Your portfolio is performing well with minor rebalancing needed"
      key_highlights:
        - "Total value: $512,450 (+8.2% YTD)"
        - "Outperforming benchmark by 1.1%"
        - "Risk level appropriate for your profile"
        - "House deposit goal: 92% funded"
        - "Action needed: Rebalance Australian equities"

    portfolio_snapshot:
      total_value: 512450
      total_value_formatted: "$512,450"
      holdings_count: 12
      last_updated: "2024-12-20T16:00:00+11:00"

    allocation_overview:
      chart_data:
        - category: "Australian Shares"
          weight: 44.5
          target: 40.0
          status: "Overweight"
        - category: "International Shares"
          weight: 26.2
          target: 30.0
          status: "Underweight"
        - category: "Bonds"
          weight: 19.8
          target: 20.0
          status: "On target"
        - category: "Cash"
          weight: 9.5
          target: 10.0
          status: "On target"
      narrative: |
        Your portfolio is slightly overweight Australian shares (+4.5%)
        and underweight international shares (-3.8%). This has been
        beneficial this year as Australian markets outperformed, but
        consider rebalancing to maintain diversification.

    performance_summary:
      returns:
        mtd: 1.2
        qtd: 3.5
        ytd: 8.2
        since_inception: 24.5
        annualised: 7.8
      vs_benchmark:
        benchmark_name: "60/40 Balanced Index"
        benchmark_return: 7.1
        relative_return: 1.1
        verdict: "Outperforming"
      narrative: |
        Strong year-to-date performance of 8.2%, ahead of the benchmark
        by 1.1%. Your Australian equity overweight contributed positively.
        Since inception (3 years), you've achieved 7.8% p.a.

    risk_assessment:
      risk_score: 6.5
      risk_category: "Moderate-Growth"
      key_metrics:
        volatility: 13.2
        max_drawdown: -18.2
        sharpe_ratio: 0.68
      concerns:
        - "Single stock (CBA) approaching 10% concentration limit"
      narrative: |
        Your portfolio risk is appropriate for your moderate risk
        tolerance and 10-year horizon. Current volatility of 13.2%
        is typical for a balanced-growth portfolio.

    goal_progress:
      - goal_name: "House Deposit"
        target: 150000
        current: 138000
        progress_pct: 92
        on_track: true
        note: "On track for June 2027"
      - goal_name: "Retirement"
        target: 1500000
        current: 374450
        progress_pct: 25
        on_track: true
        note: "Tracking to plan for 2045"

    action_items:
      - priority: "medium"
        action: "Reduce Australian equities by ~$23,000"
        rationale: "Bring back to 40% target weight"
        deadline: "Next contribution date"
      - priority: "low"
        action: "Review CBA position size"
        rationale: "Approaching 10% single-stock limit"
        deadline: "Q1 2025"

    outlook:
      market_commentary: |
        Markets have been resilient in 2024. Interest rate trajectory
        remains the key factor to watch in 2025.
      portfolio_positioning: |
        Your current allocation is well-positioned for various outcomes.
        The bond allocation provides some protection if rates stay higher.
      recommendations:
        - "Maintain current strategy"
        - "Rebalance when drift exceeds 5%"
        - "Continue regular contributions"

  formatted_report: |
    # Portfolio Health Report
    **Generated:** 20 December 2024 | **Period:** Year to Date

    ## 📊 Executive Summary

    **Health Score: 78/100** — Good

    > Your portfolio is performing well with minor rebalancing needed

    ### Key Highlights
    - Total value: **$512,450** (+8.2% YTD)
    - Outperforming benchmark by 1.1%
    - Risk level appropriate for your profile
    - House deposit goal: 92% funded
    - ⚠️ Action needed: Rebalance Australian equities

    ---

    ## 💰 Portfolio Snapshot

    | Metric | Value |
    |--------|-------|
    | Total Value | $512,450 |
    | Holdings | 12 |
    | YTD Return | +8.2% |

    ...
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Missing data for section | Omit section, note in report |
| Calculation error | Use available data, flag issue |
| Format conversion fails | Fall back to markdown |
| Stale data | Warn in report header |
