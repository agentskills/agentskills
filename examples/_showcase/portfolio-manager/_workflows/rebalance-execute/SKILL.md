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

## Execution Trace Example

The following trace shows a complete rebalance workflow with state transitions,
human checkpoints, and timing information.

```yaml
execution_trace:
  id: "RB-20241220-001"
  started: "2024-12-20T09:00:00Z"
  completed: "2024-12-20T10:25:00Z"
  final_state: COMPLETE

  transitions:
    - seq: 1
      timestamp: "2024-12-20T09:00:00Z"
      from_state: null
      to_state: MONITORING
      trigger: workflow_started
      duration_ms: 0
      notes: "Workflow initiated by scheduler"

    - seq: 2
      timestamp: "2024-12-20T09:00:05Z"
      from_state: MONITORING
      to_state: DRIFT_DETECTED
      trigger: threshold_breached
      duration_ms: 5000
      skill_used: drift-monitor
      skill_output:
        drift_detected: true
        max_drift_pct: 6.0
        asset_class: "australian_equities"
        direction: "overweight"

    - seq: 3
      timestamp: "2024-12-20T09:00:06Z"
      from_state: DRIFT_DETECTED
      to_state: ANALYSIS
      trigger: proceed_to_analysis
      duration_ms: 1000
      notes: "Auto-proceeded (drift > 5% threshold)"

    - seq: 4
      timestamp: "2024-12-20T09:00:15Z"
      from_state: ANALYSIS
      to_state: TRADE_GENERATION
      trigger: analysis_complete
      duration_ms: 9000
      skill_used: portfolio-summarise
      skill_output:
        total_value: 500000
        allocation:
          australian_equities: 0.46  # Over target of 0.40
          international_equities: 0.32
          fixed_income: 0.15
          cash: 0.07

    - seq: 5
      timestamp: "2024-12-20T09:00:35Z"
      from_state: TRADE_GENERATION
      to_state: TAX_REVIEW
      trigger: trades_generated
      duration_ms: 20000
      skill_used: trade-list-generate
      skill_output:
        trade_count: 2
        trades:
          - action: SELL
            security: CBA.AX
            quantity: 35
            estimated_value: 4987.50
          - action: BUY
            security: VGS.AX
            quantity: 52
            estimated_value: 4953.60

    - seq: 6
      timestamp: "2024-12-20T09:00:45Z"
      from_state: TAX_REVIEW
      to_state: TRADE_APPROVAL
      trigger: tax_reviewed
      duration_ms: 10000
      skill_used: tax-impact-estimate
      skill_output:
        total_gain: 825
        tax_liability: 175
        lot_selection: "hifo"
        recommendation: "proceed"

    - seq: 7
      timestamp: "2024-12-20T09:00:45Z"
      from_state: TRADE_APPROVAL
      to_state: TRADE_APPROVAL  # Waiting
      trigger: awaiting_approval
      duration_ms: 4455000  # 74 minutes
      human_checkpoint:
        presented_at: "2024-12-20T09:00:45Z"
        title: "Rebalance Approval Required"
        data_shown:
          - current_allocation
          - proposed_trades
          - tax_impact
          - expected_result
        reminder_sent: false

    - seq: 8
      timestamp: "2024-12-20T10:15:00Z"
      from_state: TRADE_APPROVAL
      to_state: EXECUTION
      trigger: approved
      duration_ms: 0
      human_checkpoint:
        decision: "approve"
        decided_by: "user@example.com"
        notes: "Approved via mobile app"

    - seq: 9
      timestamp: "2024-12-20T10:22:00Z"
      from_state: EXECUTION
      to_state: VERIFICATION
      trigger: all_executed
      duration_ms: 420000  # 7 minutes
      skill_used: trade-order-execute
      skill_output:
        trades_attempted: 2
        trades_successful: 2
        execution_details:
          - order_id: "ORD-001"
            status: "filled"
            fill_price: 142.50
            fill_time: "10:18:32"
          - order_id: "ORD-002"
            status: "filled"
            fill_price: 95.26
            fill_time: "10:21:45"

    - seq: 10
      timestamp: "2024-12-20T10:25:00Z"
      from_state: VERIFICATION
      to_state: COMPLETE
      trigger: verified
      duration_ms: 180000  # 3 minutes
      skill_used: portfolio-summarise
      skill_output:
        new_allocation:
          australian_equities: 0.40  # Now at target
          international_equities: 0.38
          fixed_income: 0.15
          cash: 0.07
        drift_from_target: 0.0

  summary:
    total_states_visited: 10
    human_checkpoints: 1
    skills_invoked: 6
    trades_executed: 2
    total_duration: "1h 25m"
    time_in_approval: "1h 14m"
    time_in_execution: "7m"
```

### Human Checkpoint Dialog Example

When the workflow reaches `TRADE_APPROVAL`, the following is presented:

```
┌─────────────────────────────────────────────────────────────┐
│                  REBALANCE APPROVAL REQUIRED                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Drift Detected: Australian Equities overweight by 6%      │
│                                                             │
│  PROPOSED TRADES:                                           │
│  ┌────────┬──────────┬─────────┬───────────┐               │
│  │ Action │ Security │   Qty   │   Value   │               │
│  ├────────┼──────────┼─────────┼───────────┤               │
│  │  SELL  │  CBA.AX  │    35   │  $4,987   │               │
│  │  BUY   │  VGS.AX  │    52   │  $4,954   │               │
│  └────────┴──────────┴─────────┴───────────┘               │
│                                                             │
│  TAX IMPACT:                                                │
│  • Capital gain: $825 (long-term)                          │
│  • Estimated tax: $175                                      │
│  • Net transaction cost: $195                               │
│                                                             │
│  EXPECTED RESULT:                                           │
│  Australian Equities: 46% → 40% (at target)                │
│  International: 32% → 38%                                   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ APPROVE  │  │  MODIFY  │  │  REJECT  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Error Recovery Trace

Example of partial execution failure and recovery:

```yaml
error_recovery_trace:
  - seq: 9
    timestamp: "2024-12-20T10:18:00Z"
    from_state: EXECUTION
    to_state: PARTIAL_EXECUTION
    trigger: some_failed
    error:
      failed_trade: "ORD-002"
      reason: "Insufficient liquidity"
      trades_completed: 1
      trades_failed: 1

  - seq: 10
    timestamp: "2024-12-20T10:18:05Z"
    from_state: PARTIAL_EXECUTION
    to_state: EXECUTION
    trigger: retry_failed
    action_taken: "Changed order type to MARKET"

  - seq: 11
    timestamp: "2024-12-20T10:20:00Z"
    from_state: EXECUTION
    to_state: VERIFICATION
    trigger: all_executed
    notes: "Retry successful with market order"
```
