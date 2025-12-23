# ips-define

Define an Investment Policy Statement (IPS).

```yaml
name: ips-define
version: 1.0.0
level: 2
category: policy-controls
operation: WRITE

description: >
  Create or update an Investment Policy Statement documenting
  investment objectives, risk limits, permitted instruments,
  ESG rules, and liquidity requirements.

requires_approval: true
approval_context: "IPS changes affect all portfolio decisions"
```

## Input Schema

```yaml
input:
  mode:
    type: enum
    values: [create, update, review]
    default: create

  existing_ips:
    type: object
    description: Current IPS if updating

  investor_info:
    type: object
    required: true
    properties:
      name: string
      type: enum [individual, joint, trust, smsf, company]
      age: number
      retirement_age: number
      dependents: number
      employment_status: string

  objectives:
    type: object
    properties:
      primary_goal: string
      secondary_goals: array
      return_objective:
        type: enum
        values: [capital_preservation, income, balanced, growth, aggressive_growth]
      return_target: number
      income_requirement: number

  risk_parameters:
    type: object
    properties:
      risk_tolerance:
        type: enum
        values: [very_low, low, moderate, high, very_high]
      risk_capacity:
        type: enum
        values: [limited, moderate, substantial]
      max_acceptable_loss: number
      volatility_tolerance: number

  constraints:
    type: object
    properties:
      time_horizon: string
      liquidity_needs:
        emergency_months: number
        planned_withdrawals: array
      tax_considerations:
        marginal_rate: number
        structures: array  # super, trust, etc.
      legal_restrictions: array
      unique_circumstances: array

  investment_guidelines:
    type: object
    properties:
      permitted_asset_classes: array
      prohibited_investments: array
      geographic_limits: object
      sector_limits: object
      position_limits: object

  esg_preferences:
    type: object
    properties:
      approach: enum [none, exclusions, best_in_class, impact]
      exclusions: array
      positive_screens: array
      engagement_preference: string

  governance:
    type: object
    properties:
      review_frequency: string
      rebalancing_approach: string
      decision_authority: string
      reporting_requirements: array
```

## Output Schema

```yaml
output:
  ips_document:
    version: string
    effective_date: date
    next_review_date: date

    sections:
      executive_summary:
        investor_profile: string
        investment_objective: string
        risk_profile: string

      investor_profile:
        personal_details: object
        financial_situation: object
        investment_experience: string

      investment_objectives:
        primary_objective: string
        return_requirements:
          target_return: number
          minimum_return: number
          income_requirement: number
        time_horizon: string
        priority_ranking: array

      risk_management:
        risk_tolerance: string
        risk_capacity: string
        risk_budget:
          max_volatility: number
          max_drawdown: number
          var_limit: number
        specific_risks:
          concentration_limits: object
          currency_limits: object
          liquidity_requirements: object

      asset_allocation:
        strategic_allocation:
          type: array
          items:
            asset_class: string
            target: number
            range_min: number
            range_max: number
        rebalancing_policy:
          trigger: string
          frequency: string
          method: string

      investment_guidelines:
        permitted_investments:
          type: array
          items:
            asset_class: string
            instruments: array
            restrictions: array
        prohibited_investments:
          type: array
        position_limits:
          single_security: number
          single_issuer: number
          single_sector: number
        quality_requirements:
          min_credit_rating: string
          min_market_cap: string

      esg_policy:
        approach: string
        exclusion_list: array
        positive_criteria: array
        engagement_expectations: string

      monitoring_reporting:
        review_frequency: string
        performance_benchmark: string
        reporting_schedule: array
        exception_reporting: array

      governance:
        decision_authority: object
        amendment_process: string
        signatures: array

  validation_notes:
    type: array
    description: Any issues or recommendations

  next_steps:
    type: array
```

## IPS Template Sections

```yaml
template_structure:
  1_executive_summary:
    purpose: "One-page overview of key elements"
    length: "250 words max"

  2_investor_profile:
    content:
      - Personal and financial situation
      - Investment experience and knowledge
      - Relevant circumstances

  3_investment_objectives:
    content:
      - Return objectives (real vs nominal)
      - Income requirements
      - Time horizon
      - Priority ranking of goals

  4_risk_management:
    content:
      - Risk tolerance (willingness)
      - Risk capacity (ability)
      - Specific risk limits
      - Downside protection requirements

  5_asset_allocation:
    content:
      - Strategic allocation targets
      - Permitted ranges
      - Rebalancing policy

  6_investment_guidelines:
    content:
      - Permitted investments
      - Prohibited investments
      - Quality requirements
      - Concentration limits

  7_esg_policy:
    content:
      - Approach to responsible investing
      - Exclusions
      - Positive screens
      - Engagement expectations

  8_monitoring_reporting:
    content:
      - Review frequency
      - Performance benchmarks
      - Reporting requirements

  9_governance:
    content:
      - Decision authority
      - Amendment process
      - Signatures and dates
```

## Example Output (Excerpt)

```yaml
output:
  ips_document:
    version: "1.0"
    effective_date: "2024-12-20"
    next_review_date: "2025-12-20"

    sections:
      executive_summary:
        investor_profile: |
          Individual investor, age 45, moderate risk tolerance,
          15-year investment horizon targeting retirement at 60.
        investment_objective: |
          Achieve real return of 4% p.a. to fund retirement income
          of $80,000 p.a. (today's dollars) from age 60.
        risk_profile: |
          Moderate risk tolerance with substantial risk capacity.
          Willing to accept short-term volatility for long-term growth.

      risk_management:
        risk_tolerance: "Moderate"
        risk_capacity: "Substantial"
        risk_budget:
          max_volatility: 15.0
          max_drawdown: 25.0
          var_limit: 3.0
        specific_risks:
          concentration_limits:
            single_security: 10
            single_sector: 30
            single_country: 50
          currency_limits:
            unhedged_foreign: 40
          liquidity_requirements:
            minimum_liquid_pct: 80
            emergency_buffer_months: 6

      asset_allocation:
        strategic_allocation:
          - asset_class: "Australian Equities"
            target: 30
            range_min: 25
            range_max: 35
          - asset_class: "International Equities"
            target: 35
            range_min: 30
            range_max: 40
          - asset_class: "Fixed Income"
            target: 25
            range_min: 20
            range_max: 30
          - asset_class: "Cash"
            target: 10
            range_min: 5
            range_max: 15
        rebalancing_policy:
          trigger: "5% absolute drift from target"
          frequency: "Quarterly review, rebalance if needed"
          method: "Cash flow directed to underweight assets first"

      esg_policy:
        approach: "Exclusions with best-in-class overlay"
        exclusion_list:
          - "Tobacco manufacturing"
          - "Controversial weapons"
          - "Thermal coal (>10% revenue)"
        positive_criteria:
          - "Companies with strong governance"
          - "Climate transition leaders"
        engagement_expectations: |
          Support shareholder resolutions on climate disclosure
          and executive remuneration alignment.

  validation_notes:
    - "Return target of 4% real is achievable with proposed allocation"
    - "Recommend reviewing ESG exclusions annually"

  next_steps:
    - "Review and sign IPS document"
    - "Implement strategic asset allocation"
    - "Set up monitoring dashboard"
    - "Schedule annual review for December 2025"
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Conflicting objectives | Flag, request clarification |
| Unrealistic return target | Model alternatives, warn |
| Missing required fields | Request input |
| Invalid constraints | Validate, suggest corrections |
