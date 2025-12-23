# rebalance-execute

End-to-end rebalancing workflow from detection to execution.

```yaml
name: rebalance-execute
version: 1.0.0
level: 3
category: workflow
operation: WRITE

description: >
  Complete rebalancing workflow: detect drift, analyse current state,
  generate optimised trade list, get approval, execute trades, and
  confirm new allocation. Includes tax optimisation and constraint
  checking throughout.

state_machine: true
human_checkpoints: [trade_approval]
requires_approval: true

composes:
  - drift-monitor
  - portfolio-summarise
  - trade-list-generate
  - tax-impact-estimate
  - constraint-validate
  - trade-order-execute
  - alert-send
  - health-report-generate
```

## State Machine

```yaml
states:
  MONITORING:
    description: "Checking portfolio for rebalance triggers"
    transitions:
      - to: DRIFT_DETECTED
        trigger: threshold_breached
      - to: SCHEDULED_REBALANCE
        trigger: calendar_trigger
      - to: MONITORING
        trigger: no_action_needed

  DRIFT_DETECTED:
    description: "Drift threshold exceeded, analysis needed"
    transitions:
      - to: ANALYSIS
        trigger: proceed_to_analysis
      - to: DEFERRED
        trigger: defer_rebalance

  SCHEDULED_REBALANCE:
    description: "Calendar-triggered rebalance check"
    transitions:
      - to: ANALYSIS
        trigger: proceed
      - to: MONITORING
        trigger: no_changes_needed

  DEFERRED:
    description: "Rebalance deferred for later"
    transitions:
      - to: MONITORING
        trigger: resume_monitoring
      - to: ANALYSIS
        trigger: proceed_now

  ANALYSIS:
    description: "Analysing current portfolio state"
    transitions:
      - to: TRADE_GENERATION
        trigger: analysis_complete

  TRADE_GENERATION:
    description: "Generating optimised trade list"
    transitions:
      - to: TAX_REVIEW
        trigger: trades_generated
      - to: NO_TRADES_NEEDED
        trigger: within_tolerance

  NO_TRADES_NEEDED:
    description: "Portfolio within acceptable bands"
    transitions:
      - to: MONITORING
        trigger: return_to_monitoring

  TAX_REVIEW:
    description: "Reviewing tax implications"
    transitions:
      - to: TRADE_APPROVAL
        trigger: tax_reviewed
      - to: TRADE_GENERATION
        trigger: regenerate_for_tax

  TRADE_APPROVAL:
    description: "Awaiting human approval of trades"
    human_checkpoint: true
    timeout_hours: 48
    transitions:
      - to: EXECUTION
        trigger: approved
      - to: TRADE_GENERATION
        trigger: modify_trades
      - to: CANCELLED
        trigger: rejected
      - to: TRADE_APPROVAL
        trigger: timeout
        action: send_reminder

  EXECUTION:
    description: "Executing approved trades"
    transitions:
      - to: VERIFICATION
        trigger: all_executed
      - to: PARTIAL_EXECUTION
        trigger: some_failed
      - to: EXECUTION_FAILED
        trigger: all_failed

  PARTIAL_EXECUTION:
    description: "Some trades failed, deciding next steps"
    transitions:
      - to: EXECUTION
        trigger: retry_failed
      - to: VERIFICATION
        trigger: proceed_with_partial
      - to: MANUAL_INTERVENTION
        trigger: escalate

  EXECUTION_FAILED:
    description: "Trade execution failed"
    transitions:
      - to: EXECUTION
        trigger: retry
      - to: MANUAL_INTERVENTION
        trigger: escalate
      - to: CANCELLED
        trigger: abort

  MANUAL_INTERVENTION:
    description: "Requires human intervention"
    human_checkpoint: true
    transitions:
      - to: EXECUTION
        trigger: issue_resolved
      - to: CANCELLED
        trigger: abort

  VERIFICATION:
    description: "Verifying new portfolio state"
    transitions:
      - to: COMPLETE
        trigger: verified
      - to: RECONCILIATION_NEEDED
        trigger: discrepancy

  RECONCILIATION_NEEDED:
    description: "Portfolio doesn't match expected state"
    transitions:
      - to: VERIFICATION
        trigger: reconciled
      - to: MANUAL_INTERVENTION
        trigger: escalate

  COMPLETE:
    description: "Rebalance successfully completed"
    terminal: true

  CANCELLED:
    description: "Rebalance cancelled"
    terminal: true
```

## Input Schema

```yaml
input:
  trigger:
    type: object
    properties:
      type: enum [drift, calendar, manual, contribution, withdrawal]
      details: object

  portfolio:
    type: object
    description: Current portfolio or reference

  target_allocation:
    type: object
    description: Target to rebalance toward

  rebalance_config:
    type: object
    properties:
      tolerance_band:
        type: number
        default: 5
        description: Acceptable drift from target (%)

      min_trade_size:
        type: number
        default: 500

      tax_optimisation:
        type: boolean
        default: true

      lot_selection:
        type: enum
        values: [fifo, lifo, hifo, tax_optimal]
        default: tax_optimal

      execution_style:
        type: enum
        values: [immediate, vwap, limit]
        default: limit

  constraints:
    type: object
    properties:
      max_tax_impact: number
      avoid_short_term_gains: boolean
      wash_sale_check: boolean
```

## Output Schema

```yaml
output:
  rebalance_id:
    type: string

  final_state:
    type: string

  trigger_details:
    type: object

  before:
    portfolio_summary: object
    drift_report: object

  trades_proposed:
    type: array
    items:
      trade: object
      rationale: string

  trades_executed:
    type: array
    items:
      trade: object
      execution_details: object
      status: string

  after:
    portfolio_summary: object
    vs_target: object

  costs:
    commissions: number
    tax_impact: number
    total_cost: number

  timeline:
    triggered: datetime
    analysis_complete: datetime
    approved: datetime
    execution_start: datetime
    execution_complete: datetime
    verified: datetime
    total_duration: string

  report:
    type: string
    description: Summary report of rebalance
```

## Workflow Steps

```yaml
workflow:
  step_1_check_trigger:
    skill: drift-monitor
    input:
      portfolio: ${input.portfolio}
      thresholds: ${input.rebalance_config}
    output: drift_report
    decision:
      - condition: drift_report.rebalance_needed
        next: step_2_analyse
      - condition: not drift_report.rebalance_needed
        next: complete_no_action

  step_2_analyse:
    skill: portfolio-summarise
    input:
      portfolio: ${input.portfolio}
    output: current_state
    next: step_3_generate_trades

  step_3_generate_trades:
    skill: trade-list-generate
    input:
      current_portfolio: ${current_state}
      target_allocation: ${input.target_allocation}
      constraints: ${input.constraints}
      optimisation_goals:
        - minimise_tax
        - minimise_trades
    output: proposed_trades
    next: step_4_tax_analysis

  step_4_tax_analysis:
    skill: tax-impact-estimate
    input:
      proposed_trades: ${proposed_trades.trade_list}
      tax_profile: ${investor.tax_profile}
    output: tax_impact
    decision:
      - condition: tax_impact.exceeds_limit
        next: step_3_generate_trades  # Regenerate with tighter constraints
      - condition: not tax_impact.exceeds_limit
        next: step_5_constraint_check

  step_5_constraint_check:
    skill: constraint-validate
    input:
      proposed_trades: ${proposed_trades}
      constraints: ${input.constraints}
    output: validation_result
    decision:
      - condition: validation_result.all_passed
        next: step_6_approval
      - condition: not validation_result.all_passed
        next: handle_constraint_violation

  step_6_approval:
    type: human_checkpoint
    present:
      title: "Rebalance Approval Required"
      current_allocation: ${current_state.allocation}
      proposed_trades: ${proposed_trades.trade_list}
      tax_impact: ${tax_impact.summary}
      expected_result: ${proposed_trades.allocation_result.after}
    decisions:
      - name: approve
        next: step_7_execute
      - name: modify
        action: update_trades
        next: step_3_generate_trades
      - name: reject
        next: cancelled

  step_7_execute:
    skill: trade-order-execute
    sequential: true  # Execute one at a time
    input:
      trades: ${proposed_trades.trade_list}
      execution_style: ${input.rebalance_config.execution_style}
    output: execution_results
    on_partial_failure:
      next: handle_partial_execution
    on_success:
      next: step_8_verify

  step_8_verify:
    skill: portfolio-summarise
    input:
      portfolio: refresh  # Fetch fresh data
    output: new_state
    next: step_9_reconcile

  step_9_reconcile:
    action: compare
    input:
      expected: ${proposed_trades.allocation_result.after}
      actual: ${new_state.allocation}
    threshold: 0.5  # % tolerance
    on_match:
      next: step_10_report
    on_mismatch:
      next: handle_reconciliation

  step_10_report:
    parallel:
      - skill: health-report-generate
        input:
          portfolio: ${new_state}
          context: "Post-rebalance"
        output: report

      - skill: alert-send
        input:
          alert:
            type: "rebalance_complete"
            title: "Rebalance completed successfully"
            data:
              trades_count: ${execution_results.count}
              total_value: ${execution_results.total_value}
    terminal: true
```

## Example Execution

```yaml
example:
  trigger:
    type: "drift"
    details:
      australian_equities:
        target: 40
        current: 46
        drift: 6

  proposed_trades:
    - action: sell
      security: "CBA.AX"
      quantity: 35
      value: 4987.50
      rationale: "Reduce financials overweight"
    - action: buy
      security: "VGS.AX"
      quantity: 52
      value: 4953.60
      rationale: "Increase international to target"

  tax_impact:
    total_gain: 825
    tax_liability: 175
    net_cost: 195  # Including commissions

  timeline:
    triggered: "2024-12-20T09:00:00"
    approved: "2024-12-20T10:15:00"
    execution_complete: "2024-12-20T10:22:00"
    verified: "2024-12-20T10:25:00"
    total_duration: "1h 25m"
```

## Error Handling

| State | Error | Recovery |
|-------|-------|----------|
| EXECUTION | Order rejected | Retry with market order |
| EXECUTION | Insufficient funds | Cancel remaining buys |
| VERIFICATION | Price moved significantly | Accept if within 2% |
| TRADE_APPROVAL | Timeout | Send reminder, extend 24h |
