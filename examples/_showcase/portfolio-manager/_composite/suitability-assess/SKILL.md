# suitability-assess

Assess if portfolio is suitable for investor's goals, horizon, and risk tolerance.

```yaml
name: suitability-assess
version: 1.0.0
level: 2
category: goal-alignment
operation: READ

description: >
  Evaluate whether current portfolio is appropriate for the investor's
  stated goals, investment horizon, and risk tolerance. Identifies
  misalignments and suggests adjustments.

composes:
  - portfolio-summarise
  - risk-profile-estimate
```

## Input Schema

```yaml
input:
  portfolio:
    type: object

  investor_profile:
    type: object
    required: true
    properties:
      goals:
        type: array
        items:
          name: string
          target_amount: number
          target_date: date
          priority: enum [essential, important, aspirational]
          flexibility: enum [fixed, somewhat_flexible, very_flexible]

      investment_horizon:
        type: string
        description: Primary investment timeframe
        examples: ["3Y", "5Y", "10Y", "20Y", "retirement_2045"]

      risk_tolerance:
        type: enum
        values: [very_low, low, moderate, high, very_high]

      risk_capacity:
        type: enum
        values: [limited, moderate, substantial]
        description: Financial ability to withstand losses

      income_needs:
        type: object
        properties:
          required: boolean
          amount: number
          frequency: enum [monthly, quarterly, annually]

      liquidity_needs:
        type: object
        properties:
          emergency_fund_months: number
          planned_withdrawals: array

      constraints:
        type: array
        items:
          type: string
        description: Investment restrictions (ESG, etc.)

      experience_level:
        type: enum
        values: [novice, intermediate, experienced, sophisticated]
```

## Output Schema

```yaml
output:
  suitability_score:
    overall: number  # 0-100
    category: string # Suitable, Marginally Suitable, Unsuitable

  alignment_analysis:
    risk_alignment:
      score: number
      portfolio_risk_level: string
      investor_risk_level: string
      aligned: boolean
      gap_description: string

    horizon_alignment:
      score: number
      portfolio_horizon_implied: string
      investor_horizon: string
      aligned: boolean
      gap_description: string

    goal_alignment:
      score: number
      goals_achievable: array
      goals_at_risk: array
      gap_description: string

    income_alignment:
      score: number
      portfolio_yield: number
      required_yield: number
      shortfall: number
      aligned: boolean

    liquidity_alignment:
      score: number
      liquid_assets_pct: number
      required_liquidity_pct: number
      aligned: boolean

  misalignments:
    type: array
    items:
      area: string
      severity: enum [minor, moderate, significant, critical]
      current_state: string
      required_state: string
      impact: string
      recommendation: string

  goal_projections:
    type: array
    items:
      goal_name: string
      target_amount: number
      target_date: date
      projected_amount: number
      probability_of_success: number
      shortfall_amount: number
      recommendation: string

  overall_assessment:
    verdict: string
    key_findings: array
    priority_actions: array

  regulatory_flags:
    type: array
    description: Compliance considerations
    items:
      rule: string
      status: enum [compliant, warning, violation]
      detail: string
```

## Suitability Rules

```yaml
suitability_rules:
  risk_matching:
    - if: investor.risk_tolerance == "very_low"
      then: portfolio.risk_rating <= 3
      message: "Conservative investor should have low-risk portfolio"

    - if: investor.risk_tolerance == "low"
      then: portfolio.risk_rating <= 4
      message: "Low risk tolerance requires conservative allocation"

    - if: investor.risk_tolerance == "moderate"
      then: 4 <= portfolio.risk_rating <= 6
      message: "Moderate risk tolerance suits balanced portfolio"

    - if: investor.risk_tolerance == "high"
      then: portfolio.risk_rating >= 5
      message: "High risk tolerance can support growth portfolio"

  horizon_matching:
    - if: investor.horizon < 3 years
      then: portfolio.equity_pct <= 30
      message: "Short horizon requires capital preservation"

    - if: investor.horizon < 5 years
      then: portfolio.equity_pct <= 50
      message: "Medium-short horizon limits equity exposure"

    - if: investor.horizon >= 10 years
      then: portfolio.equity_pct >= 40
      message: "Long horizon can support equity allocation"

  capacity_override:
    - if: investor.risk_capacity == "limited"
      then: portfolio.max_drawdown_expected <= 15%
      message: "Limited capacity restricts downside exposure"

  income_requirements:
    - if: investor.income_needs.required == true
      then: portfolio.yield >= investor.income_needs.yield_required
      message: "Income needs must be met by portfolio yield"

  liquidity_requirements:
    - if: investor.liquidity_needs.emergency_fund_months > 0
      then: portfolio.liquid_pct >= calculated_minimum
      message: "Liquidity buffer must be maintained"
```

## Example Output

```yaml
output:
  suitability_score:
    overall: 72
    category: "Marginally Suitable"

  alignment_analysis:
    risk_alignment:
      score: 65
      portfolio_risk_level: "Moderate-Growth (6.5)"
      investor_risk_level: "Moderate (5)"
      aligned: false
      gap_description: "Portfolio is slightly more aggressive than risk tolerance"

    horizon_alignment:
      score: 85
      portfolio_horizon_implied: "7-10 years"
      investor_horizon: "10 years (retirement 2035)"
      aligned: true
      gap_description: "Good alignment with investment horizon"

    goal_alignment:
      score: 70
      goals_achievable:
        - "Retirement income"
      goals_at_risk:
        - "House deposit (2027)"
      gap_description: "Near-term goal may not be achieved"

    income_alignment:
      score: 80
      portfolio_yield: 3.2
      required_yield: 2.5
      shortfall: 0
      aligned: true

  misalignments:
    - area: "Risk Level"
      severity: "moderate"
      current_state: "Risk rating 6.5 (Moderate-Growth)"
      required_state: "Risk rating 4-5 (Moderate)"
      impact: "Portfolio may decline more than comfortable in downturn"
      recommendation: "Reduce equity allocation by 10-15%"

    - area: "Short-term Goal Funding"
      severity: "significant"
      current_state: "100% invested in growth assets"
      required_state: "House deposit funds in low-risk assets"
      impact: "House deposit at risk if markets decline before 2027"
      recommendation: "Segregate $100k house deposit into defensive assets"

  goal_projections:
    - goal_name: "House Deposit"
      target_amount: 150000
      target_date: "2027-06-01"
      projected_amount: 142000
      probability_of_success: 65
      shortfall_amount: 8000
      recommendation: "Move target allocation to bonds/cash for certainty"

    - goal_name: "Retirement"
      target_amount: 1500000
      target_date: "2035-01-01"
      projected_amount: 1620000
      probability_of_success: 78
      shortfall_amount: 0
      recommendation: "On track, maintain current growth allocation"

  overall_assessment:
    verdict: "Portfolio requires adjustments for full suitability"
    key_findings:
      - "Risk level slightly high for stated tolerance"
      - "Near-term goal (house deposit) needs de-risking"
      - "Long-term retirement goal on track"
    priority_actions:
      - "Segregate house deposit funds to defensive allocation"
      - "Consider reducing overall equity by 10%"
      - "Review in 6 months after adjustments"
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Missing investor profile | Request required fields |
| Incomplete goals | Assess with available info, flag gaps |
| Conflicting inputs | Flag contradiction, ask for clarification |
