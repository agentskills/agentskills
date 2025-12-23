# annual-portfolio-review

Comprehensive yearly portfolio assessment and planning.

```yaml
name: annual-portfolio-review
version: 1.0.0
level: 3
category: workflow
operation: READ

description: >
  Comprehensive annual review covering performance attribution,
  risk assessment, goal progress, IPS compliance, tax planning,
  and forward-looking recommendations. Produces detailed report
  suitable for sharing with advisers.

state_machine: true
human_checkpoints: [review_presentation, action_approval]

composes:
  - portfolio-summarise
  - risk-profile-estimate
  - benchmark-compare
  - suitability-assess
  - goal-allocation-generate
  - scenario-analyse
  - tax-impact-estimate
  - ips-define
  - health-report-generate
```

## State Machine

```yaml
states:
  INITIATED:
    description: "Annual review initiated"
    transitions:
      - to: DATA_COLLECTION
        trigger: start

  DATA_COLLECTION:
    description: "Gathering all required data"
    transitions:
      - to: PERFORMANCE_ANALYSIS
        trigger: data_ready

  PERFORMANCE_ANALYSIS:
    description: "Analysing year's performance"
    transitions:
      - to: RISK_ANALYSIS
        trigger: performance_complete

  RISK_ANALYSIS:
    description: "Assessing current risk profile"
    transitions:
      - to: GOAL_REVIEW
        trigger: risk_complete

  GOAL_REVIEW:
    description: "Reviewing goal progress"
    transitions:
      - to: IPS_COMPLIANCE
        trigger: goals_reviewed

  IPS_COMPLIANCE:
    description: "Checking IPS compliance"
    transitions:
      - to: TAX_PLANNING
        trigger: compliance_checked

  TAX_PLANNING:
    description: "Reviewing tax situation and opportunities"
    transitions:
      - to: FORWARD_PLANNING
        trigger: tax_reviewed

  FORWARD_PLANNING:
    description: "Developing next year's strategy"
    transitions:
      - to: REPORT_GENERATION
        trigger: plan_developed

  REPORT_GENERATION:
    description: "Compiling comprehensive report"
    transitions:
      - to: REVIEW_PRESENTATION
        trigger: report_ready

  REVIEW_PRESENTATION:
    description: "Presenting findings to investor"
    human_checkpoint: true
    transitions:
      - to: ACTION_PLANNING
        trigger: presentation_complete
      - to: CLARIFICATION
        trigger: questions

  CLARIFICATION:
    description: "Addressing questions"
    transitions:
      - to: REVIEW_PRESENTATION
        trigger: return_to_presentation

  ACTION_PLANNING:
    description: "Developing action items"
    transitions:
      - to: ACTION_APPROVAL
        trigger: actions_proposed

  ACTION_APPROVAL:
    description: "Approving next year's actions"
    human_checkpoint: true
    transitions:
      - to: COMPLETE
        trigger: approved
      - to: ACTION_PLANNING
        trigger: modify

  COMPLETE:
    description: "Review complete, schedule next"
    terminal: true
```

## Input Schema

```yaml
input:
  portfolio:
    type: object

  review_period:
    type: object
    properties:
      start_date: date
      end_date: date

  investor_profile:
    type: object

  ips:
    type: object
    description: Investment Policy Statement

  previous_review:
    type: object
    description: Last year's review for comparison

  benchmarks:
    type: array
    default: ["60_40_BALANCED", "ASX200"]

  focus_areas:
    type: array
    description: Specific areas to emphasise
```

## Output Schema

```yaml
output:
  review_id:
    type: string

  review_period:
    start: date
    end: date

  executive_summary:
    headline: string
    key_achievements: array
    areas_of_concern: array
    primary_recommendations: array

  performance_review:
    absolute_return:
      period_return: number
      annualised: number
      total_value_change: number
    vs_benchmarks:
      type: array
      items:
        benchmark: string
        benchmark_return: number
        relative_return: number
        verdict: string
    attribution:
      asset_allocation_effect: number
      security_selection_effect: number
      interaction_effect: number
      top_contributors: array
      top_detractors: array
    quarterly_breakdown:
      type: array
    year_over_year:
      type: array

  risk_assessment:
    current_risk_profile: object
    vs_target_risk: object
    risk_events:
      type: array
      description: Notable risk events during year
    stress_test_results: object

  goal_progress:
    type: array
    items:
      goal: string
      progress: object
      projection: object
      recommendation: string

  ips_compliance:
    overall_status: enum [compliant, minor_breaches, significant_breaches]
    breaches:
      type: array
      items:
        rule: string
        breach_details: string
        remediation: string
    recommended_ips_updates: array

  tax_review:
    realised_gains_losses:
      gross_gains: number
      gross_losses: number
      net_position: number
    tax_liability_estimate: number
    opportunities:
      loss_harvesting: array
      lot_optimisation: array
      structure_recommendations: array

  forward_outlook:
    market_outlook: string
    portfolio_positioning: string
    recommended_changes:
      type: array
      items:
        category: string
        current: string
        recommended: string
        rationale: string

  action_items:
    immediate:
      type: array
    within_quarter:
      type: array
    within_year:
      type: array

  next_review:
    scheduled_date: date
    focus_areas: array

  full_report:
    type: string
    format: enum [markdown, pdf, html]

  appendices:
    holdings_detail: array
    transaction_history: array
    fee_analysis: object
    document_links: array
```

## Workflow Steps

```yaml
workflow:
  step_1_collect:
    parallel:
      - skill: portfolio-summarise
        output: current_portfolio
      - action: fetch_historical_data
        input:
          period: ${input.review_period}
        output: historical_data
      - action: fetch_transactions
        output: transactions
    next: step_2_performance

  step_2_performance:
    skill: benchmark-compare
    input:
      portfolio: ${current_portfolio}
      benchmarks: ${input.benchmarks}
      period: ${input.review_period}
    output: performance_analysis
    next: step_3_risk

  step_3_risk:
    skill: risk-profile-estimate
    input:
      portfolio: ${current_portfolio}
      lookback: "1Y"
    output: risk_analysis
    next: step_4_goals

  step_4_goals:
    skill: goal-allocation-generate
    input:
      goals: ${input.investor_profile.goals}
      portfolio: ${current_portfolio}
    output: goal_progress
    next: step_5_compliance

  step_5_compliance:
    skill: constraint-validate
    input:
      portfolio: ${current_portfolio}
      constraints: ${input.ips.constraints}
    output: compliance_check
    next: step_6_tax

  step_6_tax:
    skill: tax-impact-estimate
    input:
      transactions: ${transactions}
      holdings: ${current_portfolio.holdings}
    output: tax_analysis
    next: step_7_forward

  step_7_forward:
    parallel:
      - skill: scenario-analyse
        input:
          portfolio: ${current_portfolio}
        output: scenarios

      - skill: suitability-assess
        input:
          portfolio: ${current_portfolio}
          profile: ${input.investor_profile}
        output: suitability
    next: step_8_compile

  step_8_compile:
    skill: health-report-generate
    input:
      context: "Annual Review"
      all_analyses:
        - performance: ${performance_analysis}
        - risk: ${risk_analysis}
        - goals: ${goal_progress}
        - compliance: ${compliance_check}
        - tax: ${tax_analysis}
        - forward: ${scenarios}
      format: ${input.report_format}
    output: full_report
    next: step_9_present

  step_9_present:
    type: human_checkpoint
    present:
      title: "Annual Portfolio Review"
      report: ${full_report}
      key_findings:
        - performance_summary
        - risk_changes
        - goals_status
        - recommendations
    decisions:
      - name: acknowledge
        next: step_10_actions
      - name: questions
        next: clarification_loop

  step_10_actions:
    action: generate_action_plan
    input:
      all_recommendations:
        - from_suitability
        - from_goals
        - from_tax
        - from_compliance
    output: action_plan
    next: step_11_approve

  step_11_approve:
    type: human_checkpoint
    present:
      title: "Action Plan Approval"
      action_items: ${action_plan}
      implementation_timeline: true
    decisions:
      - name: approve_all
        next: step_12_complete
      - name: approve_partial
        params: selected_actions
        next: step_12_complete
      - name: modify
        next: step_10_actions

  step_12_complete:
    parallel:
      - action: save_review_record
      - action: schedule_next_review
        input:
          date: ${next_review_date}
      - action: generate_summary_email
    terminal: true
```

## Example Report Sections

```yaml
report_sections:
  1_executive_summary:
    length: "1 page"
    content:
      - Year at a glance (return, vs benchmark)
      - Key achievements
      - Areas of concern
      - Top 3 recommendations

  2_performance_deep_dive:
    length: "2-3 pages"
    content:
      - Absolute and relative returns
      - Attribution analysis
      - Quarterly breakdown
      - Best/worst positions

  3_risk_assessment:
    length: "1-2 pages"
    content:
      - Current risk metrics
      - Changes from last year
      - Risk events analysis
      - Forward-looking stress tests

  4_goal_progress:
    length: "1-2 pages"
    content:
      - Goal-by-goal status
      - Projections
      - Recommendations per goal

  5_compliance_tax:
    length: "1 page"
    content:
      - IPS compliance status
      - Tax position
      - Opportunities

  6_forward_outlook:
    length: "1-2 pages"
    content:
      - Market outlook
      - Portfolio positioning
      - Strategic recommendations

  7_action_plan:
    length: "1 page"
    content:
      - Prioritised actions
      - Timeline
      - Next review date

  appendices:
    content:
      - Holdings detail
      - Transaction list
      - Fee breakdown
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Missing historical data | Use available period |
| Benchmark unavailable | Use closest alternative |
| IPS not found | Create basic from profile |
| Report generation timeout | Deliver partial, complete async |
