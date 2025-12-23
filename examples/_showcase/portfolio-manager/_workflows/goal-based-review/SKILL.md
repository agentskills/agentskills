# goal-based-review

Periodic review of goal progress and reallocation recommendations.

```yaml
name: goal-based-review
version: 1.0.0
level: 3
category: workflow
operation: READ

description: >
  Structured review of progress toward financial goals. Analyses
  current trajectory, identifies goals at risk, and recommends
  allocation or contribution adjustments to stay on track.

state_machine: true
human_checkpoints: [review_findings, action_decision]

composes:
  - portfolio-summarise
  - goal-allocation-generate
  - suitability-assess
  - scenario-analyse
  - trade-list-generate
  - health-report-generate
```

## State Machine

```yaml
states:
  INITIATED:
    description: "Review started"
    transitions:
      - to: DATA_GATHERING
        trigger: start

  DATA_GATHERING:
    description: "Collecting portfolio and goal data"
    transitions:
      - to: PROGRESS_ANALYSIS
        trigger: data_ready

  PROGRESS_ANALYSIS:
    description: "Analysing progress toward each goal"
    transitions:
      - to: TRAJECTORY_MODELLING
        trigger: analysis_complete

  TRAJECTORY_MODELLING:
    description: "Projecting future outcomes"
    transitions:
      - to: GAP_IDENTIFICATION
        trigger: projections_ready

  GAP_IDENTIFICATION:
    description: "Identifying goals at risk"
    transitions:
      - to: RECOMMENDATION_GENERATION
        trigger: gaps_identified
      - to: ALL_ON_TRACK
        trigger: no_gaps

  ALL_ON_TRACK:
    description: "All goals on track, minimal action needed"
    transitions:
      - to: REVIEW_FINDINGS
        trigger: proceed

  RECOMMENDATION_GENERATION:
    description: "Generating corrective recommendations"
    transitions:
      - to: REVIEW_FINDINGS
        trigger: recommendations_ready

  REVIEW_FINDINGS:
    description: "Present findings to investor"
    human_checkpoint: true
    transitions:
      - to: ACTION_PLANNING
        trigger: findings_acknowledged
      - to: CLARIFICATION
        trigger: questions_raised

  CLARIFICATION:
    description: "Addressing investor questions"
    transitions:
      - to: REVIEW_FINDINGS
        trigger: clarified

  ACTION_PLANNING:
    description: "Determining actions to take"
    transitions:
      - to: ACTION_DECISION
        trigger: options_presented

  ACTION_DECISION:
    description: "Investor decides on actions"
    human_checkpoint: true
    transitions:
      - to: IMPLEMENTATION
        trigger: actions_approved
      - to: DEFER
        trigger: defer_action
      - to: COMPLETE
        trigger: no_action

  IMPLEMENTATION:
    description: "Implementing approved changes"
    transitions:
      - to: COMPLETE
        trigger: implemented

  DEFER:
    description: "Actions deferred to later date"
    transitions:
      - to: COMPLETE
        trigger: reminder_set

  COMPLETE:
    description: "Review complete"
    terminal: true
```

## Input Schema

```yaml
input:
  portfolio:
    type: object

  goals:
    type: array
    required: true
    items:
      goal_id: string
      name: string
      target_amount: number
      target_date: date
      priority: enum [essential, important, aspirational]
      current_allocation: number
      contributions:
        amount: number
        frequency: string

  review_type:
    type: enum
    values: [quarterly, semi_annual, annual, triggered]
    default: quarterly

  previous_review:
    type: object
    description: Results from last review for comparison

  assumptions:
    type: object
    properties:
      expected_return: number
      inflation_rate: number
      contribution_growth: number
```

## Output Schema

```yaml
output:
  review_id:
    type: string

  review_date:
    type: date

  portfolio_summary:
    total_value: number
    since_last_review:
      return_pct: number
      return_value: number
      contributions: number

  goal_progress:
    type: array
    items:
      goal_id: string
      goal_name: string
      target_amount: number
      target_date: date
      years_remaining: number

      current_status:
        allocated_amount: number
        progress_pct: number
        on_track: boolean

      projection:
        expected_amount: number
        probability_of_success: number
        confidence_range:
          p10: number
          p50: number
          p90: number

      vs_previous_review:
        progress_change: number
        probability_change: number
        trajectory: enum [improving, stable, declining]

      risk_assessment:
        status: enum [on_track, at_risk, critical]
        primary_risk: string
        mitigation_options: array

  overall_assessment:
    goals_on_track: number
    goals_at_risk: number
    goals_critical: number
    summary: string

  recommendations:
    type: array
    items:
      goal_name: string
      recommendation_type: enum [reallocation, contribution_increase, timeline_extension, goal_reduction, no_change]
      description: string
      impact:
        probability_change: number
        new_probability: number
      implementation:
        trades: array
        contribution_change: number

  scenario_analysis:
    type: array
    items:
      scenario_name: string
      probability: number
      impact_on_goals: array

  action_options:
    type: array
    items:
      option_name: string
      description: string
      goals_addressed: array
      cost_impact: number
      probability_improvement: number

  next_review:
    recommended_date: date
    focus_areas: array
```

## Workflow Steps

```yaml
workflow:
  step_1_gather:
    parallel:
      - skill: portfolio-summarise
        output: portfolio_state
      - action: fetch_goal_history
        output: goal_history
    next: step_2_progress

  step_2_progress:
    skill: goal-allocation-generate
    input:
      goals: ${input.goals}
      portfolio: ${portfolio_state}
    output: current_goal_status
    next: step_3_project

  step_3_project:
    action: monte_carlo_projection
    input:
      goals: ${current_goal_status.goals_analysis}
      assumptions: ${input.assumptions}
      simulations: 10000
    output: projections
    next: step_4_identify_gaps

  step_4_identify_gaps:
    action: analyse_gaps
    input:
      projections: ${projections}
      threshold:
        essential: 0.90  # 90% success probability required
        important: 0.75
        aspirational: 0.50
    output: gap_analysis
    decision:
      - condition: gap_analysis.has_critical_gaps
        next: step_5_recommendations
      - condition: not gap_analysis.has_gaps
        next: step_7_present

  step_5_recommendations:
    parallel:
      - action: generate_reallocation_options
        input:
          gaps: ${gap_analysis}
          portfolio: ${portfolio_state}
        output: reallocation_options

      - action: generate_contribution_options
        input:
          gaps: ${gap_analysis}
          current_contributions: ${input.goals}
        output: contribution_options

      - action: generate_timeline_options
        input:
          gaps: ${gap_analysis}
        output: timeline_options
    next: step_6_scenarios

  step_6_scenarios:
    skill: scenario-analyse
    input:
      portfolio: ${portfolio_state}
      scenarios: [recession_mild, rate_hike_200bp, equity_bull]
    output: scenario_impact
    next: step_7_present

  step_7_present:
    type: human_checkpoint
    present:
      title: "Goal Progress Review"
      sections:
        - portfolio_performance
        - goal_by_goal_progress
        - goals_at_risk
        - recommendations
        - scenario_analysis
    output: user_questions
    next: step_8_options

  step_8_options:
    type: human_checkpoint
    present:
      title: "Action Options"
      options: ${action_options}
      comparison_table: true
    decisions:
      - name: approve_option
        params: option_id
        next: step_9_implement
      - name: defer
        next: step_10_defer
      - name: no_action
        next: step_11_complete

  step_9_implement:
    skill: trade-list-generate
    condition: selected_option.has_trades
    input:
      target_allocation: ${selected_option.new_allocation}
    output: implementation_trades
    next: step_11_complete

  step_10_defer:
    action: set_reminder
    input:
      reminder_date: ${user_specified_date}
      context: ${gap_analysis}
    next: step_11_complete

  step_11_complete:
    skill: health-report-generate
    input:
      context: "Goal Review"
      include: [goal_progress, recommendations, next_steps]
    output: review_report
    terminal: true
```

## Example Output

```yaml
output:
  review_id: "GR-20241220-001"
  review_date: "2024-12-20"

  goal_progress:
    - goal_id: "G1"
      goal_name: "House Deposit"
      target_amount: 150000
      target_date: "2027-06-01"
      years_remaining: 2.5

      current_status:
        allocated_amount: 138000
        progress_pct: 92
        on_track: true

      projection:
        expected_amount: 158000
        probability_of_success: 85
        confidence_range:
          p10: 142000
          p50: 158000
          p90: 175000

      vs_previous_review:
        progress_change: +8
        probability_change: +5
        trajectory: "improving"

      risk_assessment:
        status: "on_track"
        primary_risk: "Market downturn before goal date"
        mitigation_options:
          - "Move to defensive allocation now"
          - "Maintain current allocation for upside"

    - goal_id: "G2"
      goal_name: "Children's Education"
      target_amount: 200000
      target_date: "2035-01-01"
      years_remaining: 10

      current_status:
        allocated_amount: 45000
        progress_pct: 22.5
        on_track: false

      projection:
        expected_amount: 165000
        probability_of_success: 58
        confidence_range:
          p10: 120000
          p50: 165000
          p90: 220000

      vs_previous_review:
        progress_change: +2
        probability_change: -3
        trajectory: "declining"

      risk_assessment:
        status: "at_risk"
        primary_risk: "Insufficient contributions"
        mitigation_options:
          - "Increase contributions by $200/month"
          - "Accept 80% of target"
          - "Extend timeline by 2 years"

  overall_assessment:
    goals_on_track: 2
    goals_at_risk: 1
    goals_critical: 0
    summary: |
      House deposit on track with 85% probability. Retirement solid.
      Children's education goal at risk - contributions need to increase
      by $200/month to achieve 75% probability of success.

  recommendations:
    - goal_name: "Children's Education"
      recommendation_type: "contribution_increase"
      description: "Increase monthly contribution from $300 to $500"
      impact:
        probability_change: +17
        new_probability: 75
      implementation:
        contribution_change: +200

  action_options:
    - option_name: "Increase education contributions"
      description: "Add $200/month to education goal"
      goals_addressed: ["Children's Education"]
      cost_impact: 2400  # Per year
      probability_improvement: 17

    - option_name: "Reallocate from retirement"
      description: "Shift $20,000 from retirement to education"
      goals_addressed: ["Children's Education"]
      cost_impact: 0
      probability_improvement: 12
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Missing goal data | Use last known values |
| Projection timeout | Reduce simulation count |
| Conflicting recommendations | Present trade-offs clearly |
