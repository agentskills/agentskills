---
name: portfolio-rebalance
description: |
  Portfolio rebalancing workflow from drift detection through approval and execution.
  Monitors allocation drift, generates rebalancing recommendations, obtains approval,
  and executes trades with tax optimisation.
level: 3
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - portfolio-read
  - portfolio-analyse
  - client-data-read
  - compliance-check
  - trade-execute
state_machine: true
---

# Portfolio Rebalance

Monitor and rebalance portfolios to target allocation.

## Trigger Phrases

- "Check portfolios for rebalancing needs"
- "Rebalance [client] portfolio to target"
- "Execute rebalance for accounts with drift >5%"

## State Machine

```
┌─────────────────┐
│   MONITORING    │ ← Continuous drift monitoring
└────────┬────────┘
         │ Drift threshold exceeded
         ▼
┌─────────────────┐
│ DRIFT_DETECTED  │ ← Portfolio flagged for review
└────────┬────────┘
         │ Analysis initiated
         ▼
┌─────────────────┐
│    ANALYSIS     │ ← Determine rebalance approach
│                 │   Tax impact assessment
└────────┬────────┘
         │ Recommendation generated
         ▼
┌─────────────────┐
│    APPROVAL     │ ← Supervisor/client approval
│    PENDING      │   (based on thresholds)
└────────┬────────┘
         │ Approved
         ▼
┌─────────────────┐
│   EXECUTING     │ ← Trades being placed
└────────┬────────┘
         │ Trades complete
         ▼
┌─────────────────┐
│    COMPLETE     │ ✓ Portfolio rebalanced
└─────────────────┘
```

## Workflow Steps

```
1. MONITORING
   │ • Calculate current allocation
   │ • Compare to target
   │ • Check against drift thresholds
   │
   ▼
2. DRIFT DETECTION
   │ • Flag portfolios exceeding thresholds
   │ • Prioritise by severity
   │ • Group related accounts
   │
   ▼
3. ANALYSIS
   │ • Calculate trades needed
   │ • Assess tax implications
   │ • Identify optimal execution
   │ • Consider cash flows
   │
   ▼
4. RECOMMENDATION
   │ • Generate trade list
   │ • Estimate costs
   │ • Project post-rebalance allocation
   │
   ▼
5. APPROVAL
   │ • Determine approval level
   │ • Submit for review
   │ • Document rationale
   │
   ▼
6. EXECUTION
   │ • Submit trades
   │ • Monitor fills
   │ • Handle exceptions
   │
   ▼
7. CONFIRMATION
   │ • Verify final allocation
   │ • Update records
   │ • Notify client (if required)
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | No | Specific client (or all if blank) |
| `account_id` | string | No | Specific account |
| `force` | boolean | No | Rebalance even if within tolerance |
| `tax_aware` | boolean | No | Optimise for tax (default: true) |
| `notify_client` | boolean | No | Send notification (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `rebalance_id` | string | Rebalance batch identifier |
| `status` | string | Current workflow state |
| `portfolios` | object[] | Portfolios analysed |
| `recommendations` | object[] | Recommended trades |
| `tax_analysis` | object | Tax impact summary |
| `approval` | object | Approval status |
| `execution` | object | Trade execution results |

## Usage

```
Check all portfolios for rebalancing needs
```

```
Rebalance John Smith's investment account
```

```
Run month-end rebalancing for all growth profile clients
```

## Example Response

```json
{
  "rebalance_id": "REB-2024-12-23-001",
  "status": "COMPLETE",
  "summary": {
    "portfolios_reviewed": 45,
    "requiring_rebalance": 8,
    "rebalances_executed": 8,
    "total_trades": 24,
    "total_value_moved": 156000
  },
  "portfolios": [
    {
      "client_id": "C-12345",
      "account_id": "ACC-001",
      "pre_rebalance": {
        "australian_equities": 38.5,
        "international_equities": 26.2,
        "property": 9.8,
        "fixed_income": 17.5,
        "cash": 8.0
      },
      "target": {
        "australian_equities": 35.0,
        "international_equities": 30.0,
        "property": 10.0,
        "fixed_income": 17.0,
        "cash": 8.0
      },
      "drift": {
        "max_drift": 3.8,
        "drift_assets": ["international_equities"],
        "trigger": "threshold_exceeded"
      },
      "post_rebalance": {
        "australian_equities": 35.1,
        "international_equities": 29.9,
        "property": 10.0,
        "fixed_income": 17.0,
        "cash": 8.0
      }
    }
  ],
  "recommendations": [
    {
      "client_id": "C-12345",
      "trades": [
        {
          "action": "sell",
          "security": "VAS.ASX",
          "current_weight": 28.5,
          "target_weight": 25.0,
          "value": 11000,
          "rationale": "Reduce overweight Australian equities"
        },
        {
          "action": "buy",
          "security": "VGS.ASX",
          "current_weight": 16.2,
          "target_weight": 20.0,
          "value": 11000,
          "rationale": "Increase underweight international equities"
        }
      ]
    }
  ],
  "tax_analysis": {
    "total_portfolios": 8,
    "capital_gains_triggered": 3,
    "estimated_cgt": 2340,
    "losses_harvested": 890,
    "net_tax_impact": 1450,
    "optimisations_applied": [
      "Used losses to offset gains",
      "Prioritised shares held >12 months for discount",
      "Deferred some sales to next financial year"
    ]
  },
  "approval": {
    "level": "supervisor",
    "approved_by": "Senior Adviser",
    "approved_at": "2024-12-23T10:30:00Z",
    "notes": "Standard rebalancing, all within guidelines"
  },
  "execution": {
    "trades_submitted": 24,
    "trades_filled": 24,
    "trades_failed": 0,
    "total_brokerage": 237.60,
    "average_fill_quality": "at_or_better",
    "settlement_date": "2024-12-27"
  },
  "notifications": {
    "clients_notified": 8,
    "method": "email",
    "template": "portfolio_rebalance_notification"
  },
  "audit_reference": "REB-2024-12-23-001"
}
```

## Drift Thresholds

| Level | Threshold | Action |
|-------|-----------|--------|
| Growth/Defensive | ±5% | Mandatory rebalance |
| Asset class | ±3% | Consider rebalance |
| Single security | ±2% | Monitor, may rebalance |

## Rebalancing Approaches

| Approach | Description | When to Use |
|----------|-------------|-------------|
| Cash flow | Use inflows/outflows | Regular contributions |
| Threshold | Rebalance when exceeded | Standard monitoring |
| Calendar | Fixed schedule (quarterly) | Systematic approach |
| Tactical | Opportunistic | Market conditions |

## Tax Optimisation

| Strategy | Application |
|----------|-------------|
| Loss harvesting | Realise losses to offset gains |
| CGT discount | Prioritise assets held >12 months |
| Timing | Defer gains near year-end |
| Wash sale rules | Avoid repurchasing within 30 days |

## Approval Thresholds

| Condition | Approval Required |
|-----------|-------------------|
| Routine rebalance | Adviser |
| Trade >$50,000 | Supervisor |
| Significant tax impact | Client acknowledgment |
| Out of model | Investment committee |

## Notes

- Rebalancing checked daily for all portfolios
- Threshold breaches generate alerts
- Tax analysis included in all recommendations
- Client notification configurable by preference
- All trades linked to rebalance justification
