# goal-allocation-generate

Generate target allocations for different goals and map holdings.

```yaml
name: goal-allocation-generate
version: 1.0.0
level: 2
category: goal-alignment
operation: READ

description: >
  Create goal-specific target allocations based on goal characteristics
  (amount, timeline, priority). Maps existing holdings to goals and
  identifies funding gaps.

composes:
  - portfolio-summarise
  - risk-profile-estimate
```

## Input Schema

```yaml
input:
  goals:
    type: array
    required: true
    items:
      name:
        type: string
        required: true
      target_amount:
        type: number
        required: true
      target_date:
        type: date
        required: true
      priority:
        type: enum
        values: [essential, important, aspirational]
        default: important
      flexibility:
        type: object
        properties:
          amount: enum [fixed, somewhat_flexible, very_flexible]
          timing: enum [fixed, somewhat_flexible, very_flexible]
      current_funding:
        type: number
        description: Amount already allocated to this goal
      contributions:
        type: object
        properties:
          amount: number
          frequency: enum [weekly, fortnightly, monthly, quarterly, annually]

  portfolio:
    type: object
    description: Current portfolio to map against goals

  investor_profile:
    type: object
    properties:
      risk_tolerance: enum
      age: number

  allocation_approach:
    type: enum
    values: [bucket, unified, hybrid]
    default: bucket
    description: |
      bucket: Separate pools per goal
      unified: Single portfolio serving all goals
      hybrid: Core/satellite approach
```

## Output Schema

```yaml
output:
  goals_analysis:
    type: array
    items:
      goal_name: string
      target_amount: number
      target_date: date
      years_to_goal: number
      current_funding: number
      funding_gap: number
      required_return: number
      recommended_allocation:
        type: object
        properties:
          growth_assets: number
          defensive_assets: number
          cash: number
          specific_allocation:
            australian_equity: number
            international_equity: number
            fixed_income: number
            cash: number
      risk_level: string
      probability_of_success: number
      monte_carlo_range:
        p10: number
        p50: number
        p90: number

  portfolio_mapping:
    mapped_holdings:
      type: array
      items:
        goal_name: string
        holdings: array
        total_value: number
        alignment_score: number
    unmapped_holdings:
      type: array
      items:
        security: string
        value: number
        suggestion: string

  contribution_plan:
    type: array
    items:
      goal_name: string
      current_contribution: number
      required_contribution: number
      contribution_gap: number
      recommendation: string

  target_portfolio:
    combined_allocation:
      australian_equity: number
      international_equity: number
      fixed_income: number
      cash: number
    goal_weights:
      type: array
      items:
        goal: string
        portfolio_weight: number

  implementation_steps:
    type: array
    items:
      priority: number
      action: string
      rationale: string
```

## Allocation Rules by Goal Horizon

```yaml
horizon_based_allocation:
  # Very short term (< 2 years)
  0-2_years:
    growth_assets: 0-10
    defensive_assets: 20-40
    cash: 50-80
    rationale: "Capital preservation paramount"

  # Short term (2-5 years)
  2-5_years:
    growth_assets: 20-40
    defensive_assets: 30-50
    cash: 20-30
    rationale: "Limited time for recovery"

  # Medium term (5-10 years)
  5-10_years:
    growth_assets: 50-70
    defensive_assets: 25-40
    cash: 5-10
    rationale: "Balanced growth and protection"

  # Long term (10-20 years)
  10-20_years:
    growth_assets: 70-85
    defensive_assets: 10-25
    cash: 5
    rationale: "Time to recover from volatility"

  # Very long term (20+ years)
  20+_years:
    growth_assets: 80-95
    defensive_assets: 5-15
    cash: 0-5
    rationale: "Maximum growth exposure"
```

## Priority Adjustments

```yaml
priority_adjustments:
  essential:
    description: "Must achieve this goal (e.g., child's education)"
    risk_reduction: 10%  # More conservative
    success_target: 90%  # Higher probability required

  important:
    description: "Strongly desired goal"
    risk_reduction: 0%
    success_target: 75%

  aspirational:
    description: "Nice to have if possible"
    risk_increase: 10%  # Can be more aggressive
    success_target: 50%
```

## Example Output

```yaml
output:
  goals_analysis:
    - goal_name: "House Deposit"
      target_amount: 150000
      target_date: "2027-06-01"
      years_to_goal: 2.5
      current_funding: 80000
      funding_gap: 70000
      required_return: 5.2
      recommended_allocation:
        growth_assets: 20
        defensive_assets: 40
        cash: 40
        specific_allocation:
          australian_equity: 10
          international_equity: 10
          fixed_income: 40
          cash: 40
      risk_level: "Conservative"
      probability_of_success: 85
      monte_carlo_range:
        p10: 135000
        p50: 155000
        p90: 175000

    - goal_name: "Retirement"
      target_amount: 1500000
      target_date: "2045-01-01"
      years_to_goal: 20
      current_funding: 350000
      funding_gap: 1150000
      required_return: 7.8
      recommended_allocation:
        growth_assets: 85
        defensive_assets: 12
        cash: 3
        specific_allocation:
          australian_equity: 35
          international_equity: 50
          fixed_income: 12
          cash: 3
      risk_level: "Growth"
      probability_of_success: 72
      monte_carlo_range:
        p10: 1100000
        p50: 1650000
        p90: 2400000

    - goal_name: "Children's Education"
      target_amount: 200000
      target_date: "2035-01-01"
      years_to_goal: 10
      current_funding: 50000
      funding_gap: 150000
      required_return: 6.5
      recommended_allocation:
        growth_assets: 65
        defensive_assets: 30
        cash: 5
      risk_level: "Balanced-Growth"
      probability_of_success: 78

  portfolio_mapping:
    mapped_holdings:
      - goal_name: "House Deposit"
        holdings:
          - security: "Cash Account"
            value: 50000
          - security: "VAF.AX"
            value: 30000
        total_value: 80000
        alignment_score: 82

      - goal_name: "Retirement"
        holdings:
          - security: "VAS.AX"
            value: 150000
          - security: "VGS.AX"
            value: 200000
        total_value: 350000
        alignment_score: 88

  contribution_plan:
    - goal_name: "House Deposit"
      current_contribution: 2000
      required_contribution: 2300
      contribution_gap: 300
      recommendation: "Increase monthly by $300 or extend timeline by 4 months"

    - goal_name: "Retirement"
      current_contribution: 1500
      required_contribution: 1500
      contribution_gap: 0
      recommendation: "On track with current contributions"

  target_portfolio:
    combined_allocation:
      australian_equity: 28
      international_equity: 37
      fixed_income: 22
      cash: 13
    goal_weights:
      - goal: "House Deposit"
        portfolio_weight: 16
      - goal: "Retirement"
        portfolio_weight: 70
      - goal: "Children's Education"
        portfolio_weight: 14

  implementation_steps:
    - priority: 1
      action: "Segregate house deposit funds into defensive bucket"
      rationale: "Protect near-term goal from market volatility"
    - priority: 2
      action: "Increase house deposit contributions by $300/month"
      rationale: "Close funding gap to meet 2027 target"
    - priority: 3
      action: "Maintain current retirement allocation"
      rationale: "Growth allocation appropriate for 20-year horizon"
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Goals exceed portfolio value | Flag shortfall, prioritise goals |
| Conflicting allocations | Suggest unified or bucket approach |
| Unrealistic returns needed | Flag, suggest adjustments |
| Missing contribution data | Project based on current trajectory |
