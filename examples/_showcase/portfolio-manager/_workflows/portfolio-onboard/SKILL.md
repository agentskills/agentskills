# portfolio-onboard

Full portfolio onboarding workflow from ingestion to actionable analysis.

```yaml
name: portfolio-onboard
version: 1.0.0
level: 3
category: workflow
operation: READ  # Overall workflow is analysis, individual steps may write

description: >
  End-to-end portfolio onboarding workflow. Ingests holdings,
  enriches with market data, analyses composition and risk,
  assesses suitability, and produces comprehensive initial report.

state_machine: true
human_checkpoints: [suitability_review]

composes:
  - holdings-ingest
  - market-data-fetch
  - portfolio-summarise
  - risk-profile-estimate
  - benchmark-compare
  - suitability-assess
  - goal-allocation-generate
  - health-report-generate
```

## State Machine

```yaml
states:
  INITIATED:
    description: "Workflow started, awaiting data sources"
    transitions:
      - to: DATA_COLLECTION
        trigger: sources_provided

  DATA_COLLECTION:
    description: "Ingesting holdings from provided sources"
    transitions:
      - to: DATA_ENRICHMENT
        trigger: ingestion_complete
      - to: DATA_COLLECTION_FAILED
        trigger: ingestion_error

  DATA_COLLECTION_FAILED:
    description: "Ingestion failed, awaiting resolution"
    transitions:
      - to: DATA_COLLECTION
        trigger: retry
      - to: CANCELLED
        trigger: cancel

  DATA_ENRICHMENT:
    description: "Fetching market data and classifications"
    transitions:
      - to: ANALYSIS
        trigger: enrichment_complete
      - to: DATA_ENRICHMENT_PARTIAL
        trigger: partial_data

  DATA_ENRICHMENT_PARTIAL:
    description: "Some securities couldn't be enriched"
    transitions:
      - to: ANALYSIS
        trigger: proceed_with_available
      - to: DATA_ENRICHMENT
        trigger: retry_enrichment

  ANALYSIS:
    description: "Running portfolio analysis suite"
    transitions:
      - to: SUITABILITY_REVIEW
        trigger: analysis_complete

  SUITABILITY_REVIEW:
    description: "Human review of suitability assessment"
    human_checkpoint: true
    transitions:
      - to: REPORT_GENERATION
        trigger: suitability_approved
      - to: ANALYSIS
        trigger: rerun_with_changes
      - to: PROFILE_UPDATE_NEEDED
        trigger: profile_mismatch

  PROFILE_UPDATE_NEEDED:
    description: "Investor profile needs updating"
    transitions:
      - to: ANALYSIS
        trigger: profile_updated

  REPORT_GENERATION:
    description: "Generating comprehensive onboarding report"
    transitions:
      - to: COMPLETE
        trigger: report_ready

  COMPLETE:
    description: "Onboarding complete, portfolio ready for management"
    terminal: true

  CANCELLED:
    description: "Workflow cancelled"
    terminal: true
```

## Input Schema

```yaml
input:
  client_info:
    type: object
    required: true
    properties:
      client_id: string
      name: string
      type: enum [individual, joint, trust, smsf, company]

  data_sources:
    type: array
    required: true
    items:
      source_type: enum [csv, xlsx, api, broker_feed, manual]
      source_location: string
      broker: string
      account_name: string

  investor_profile:
    type: object
    required: true
    properties:
      goals: array
      risk_tolerance: enum
      risk_capacity: enum
      investment_horizon: string
      income_needs: object
      liquidity_needs: object
      constraints: array

  ips_reference:
    type: string
    description: Reference to existing IPS if available

  preferences:
    type: object
    properties:
      benchmark: string
      reporting_currency: string
      comparison_models: array
```

## Output Schema

```yaml
output:
  onboarding_id:
    type: string

  final_state:
    type: string

  portfolio:
    portfolio_id: string
    total_value: number
    holdings_count: number
    as_of_date: date

  analysis_results:
    summary:
      type: object
      description: Portfolio composition breakdown

    risk_profile:
      type: object
      description: Risk metrics and rating

    benchmark_comparison:
      type: object
      description: Comparison to selected benchmark

    suitability:
      type: object
      description: Alignment with investor profile

    goal_mapping:
      type: object
      description: Holdings mapped to goals

  issues_found:
    type: array
    items:
      severity: enum [critical, warning, info]
      category: string
      description: string
      recommendation: string

  action_plan:
    immediate_actions:
      type: array
      description: Actions needed now
    recommended_changes:
      type: array
      description: Suggested portfolio adjustments
    monitoring_setup:
      type: object
      description: Ongoing monitoring configuration

  report:
    format: string
    content: string
    attachments: array

  state_history:
    type: array
    items:
      state: string
      entered_at: datetime
      exited_at: datetime
      notes: string
```

## Workflow Steps

```yaml
workflow:
  step_1_initiate:
    action: "Create onboarding record"
    output: onboarding_id
    next: step_2_collect

  step_2_collect:
    skill: holdings-ingest
    parallel_execution: true  # Multiple sources can run in parallel
    input:
      sources: ${input.data_sources}
    output: raw_holdings
    on_success: step_3_enrich
    on_failure: handle_ingestion_error

  step_3_enrich:
    skill: market-data-fetch
    input:
      securities: ${raw_holdings.security_ids}
      data_types: [price, fundamentals, history]
    output: market_data
    next: step_4_analyse

  step_4_analyse:
    parallel:
      - skill: portfolio-summarise
        input:
          holdings: ${raw_holdings}
          market_data: ${market_data}
        output: summary

      - skill: risk-profile-estimate
        input:
          portfolio: ${raw_holdings}
        output: risk_profile

      - skill: benchmark-compare
        input:
          portfolio: ${raw_holdings}
          benchmark: ${input.preferences.benchmark}
        output: benchmark_comparison
    next: step_5_suitability

  step_5_suitability:
    skill: suitability-assess
    input:
      portfolio: ${summary}
      investor_profile: ${input.investor_profile}
      risk_profile: ${risk_profile}
    output: suitability
    next: step_6_checkpoint

  step_6_checkpoint:
    type: human_checkpoint
    description: "Review suitability assessment"
    present_to_user:
      - suitability.overall_score
      - suitability.misalignments
      - suitability.recommendations
    decisions:
      - name: approve
        next: step_7_goals
      - name: update_profile
        next: update_investor_profile
      - name: reanalyse
        next: step_4_analyse

  step_7_goals:
    skill: goal-allocation-generate
    input:
      goals: ${input.investor_profile.goals}
      portfolio: ${summary}
    output: goal_mapping
    next: step_8_report

  step_8_report:
    skill: health-report-generate
    input:
      portfolio: ${summary}
      risk_profile: ${risk_profile}
      suitability: ${suitability}
      goal_mapping: ${goal_mapping}
      format: ${input.preferences.report_format}
    output: report
    next: step_9_finalise

  step_9_finalise:
    action: "Compile final outputs and action plan"
    output:
      - onboarding_summary
      - action_plan
      - monitoring_config
    terminal: true
```

## Example Execution

```yaml
example:
  input:
    client_info:
      client_id: "CLI-001"
      name: "John Smith"
      type: "individual"

    data_sources:
      - source_type: "csv"
        source_location: "/uploads/commsec_holdings.csv"
        broker: "commsec"
        account_name: "Trading Account"
      - source_type: "api"
        source_location: "selfwealth://account/123"
        broker: "selfwealth"
        account_name: "SMSF"

    investor_profile:
      goals:
        - name: "Retirement"
          target: 1500000
          date: "2040-01-01"
          priority: "essential"
      risk_tolerance: "moderate"
      risk_capacity: "substantial"
      investment_horizon: "15Y"

  output:
    onboarding_id: "ONB-20241220-001"
    final_state: "COMPLETE"

    portfolio:
      portfolio_id: "PF-001"
      total_value: 523450
      holdings_count: 15
      as_of_date: "2024-12-20"

    issues_found:
      - severity: "warning"
        category: "concentration"
        description: "CBA.AX at 11.2% exceeds 10% limit"
        recommendation: "Reduce position by $6,200"
      - severity: "info"
        category: "drift"
        description: "Australian equities 5% overweight"
        recommendation: "Consider rebalancing"

    action_plan:
      immediate_actions:
        - "Reduce CBA.AX to comply with concentration limit"
        - "Set up monitoring alerts"
      recommended_changes:
        - "Rebalance to target allocation over next 3 months"
        - "Consider increasing international exposure"
```

## Error Handling

| State | Error | Recovery |
|-------|-------|----------|
| DATA_COLLECTION | Parse failure | Retry with different parser |
| DATA_COLLECTION | Source unavailable | Skip source, warn, continue |
| DATA_ENRICHMENT | Security not found | Add to unknown list, continue |
| ANALYSIS | Calculation error | Use partial results, flag |
| SUITABILITY_REVIEW | Timeout | Auto-save, remind |
