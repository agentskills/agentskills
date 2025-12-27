---
name: trade-execute
description: Execute investment trades on client portfolios. Supports buy, sell, switch, and rebalance orders with pre-trade compliance checks.
level: 1
operation: WRITE
license: Apache-2.0
domain: financial-advisory
requires_approval: true
tool_discovery:
  platform:
    prefer: [hub24-trade, netwealth-trade, praemium-trade]
    fallback: manual-trade
---

# Trade Execute

Execute investment trades with compliance verification.

## When to Use

Use this skill when:
- Implementing advice recommendations
- Rebalancing portfolios
- Processing client requests
- Adjusting asset allocation

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `account_id` | string | Yes | Account to trade in |
| `orders` | object[] | Yes | List of trade orders |
| `advice_reference` | string | No | SOA/ROA reference (if implementing advice) |
| `reason` | string | Yes | Reason for trade |
| `urgency` | string | No | Urgency: normal, same_day, immediate |

## Order Schema

```json
{
  "orders": [
    {
      "action": "buy",
      "security_id": "VAS.ASX",
      "order_type": "market",
      "amount": 10000,
      "amount_type": "value"
    },
    {
      "action": "sell",
      "security_id": "IOZ.ASX",
      "order_type": "limit",
      "units": 100,
      "limit_price": 32.50
    }
  ]
}
```

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `trade_id` | string | Unique trade batch identifier |
| `orders` | object[] | Individual order status |
| `pre_trade_checks` | object | Compliance verification results |
| `estimated_cost` | number | Total transaction costs |
| `settlement_date` | string | Expected settlement |
| `requires_approval` | boolean | Whether supervisor approval needed |

## Pre-Trade Checks

| Check | Description | Blocker |
|-------|-------------|---------|
| Suitability | Matches risk profile | Yes |
| Concentration | Within position limits | Yes |
| Cash available | Sufficient for buy orders | Yes |
| Holdings exist | Sufficient units for sell | Yes |
| Advice reference | Links to SOA/ROA if required | Warning |
| Wash sale | CGT wash sale rule | Warning |

## Usage

```
Buy $10,000 of VAS ETF in John Smith's investment account
```

```
Rebalance portfolio to target allocation for client C-12345
```

```
Sell all holdings in XYZ fund - client requested exit
```

## Example Response

```json
{
  "trade_id": "TRD-2024-12-23-001234",
  "status": "pending_approval",
  "orders": [
    {
      "order_id": "ORD-001",
      "action": "buy",
      "security": "VAS.ASX",
      "security_name": "Vanguard Australian Shares ETF",
      "order_type": "market",
      "amount": 10000,
      "estimated_units": 104.71,
      "estimated_price": 95.50,
      "status": "ready",
      "pre_trade_checks": {
        "suitability": "pass",
        "concentration": "pass",
        "cash_available": "pass"
      }
    }
  ],
  "pre_trade_summary": {
    "all_checks_passed": true,
    "warnings": [],
    "blocks": []
  },
  "estimated_cost": {
    "brokerage": 9.95,
    "platform_fee": 0,
    "total": 9.95
  },
  "settlement_date": "2024-12-27",
  "requires_approval": true,
  "approval_reason": "Trade value exceeds $5,000",
  "approval_request_sent": true
}
```

## Order Types

| Type | Description | Use Case |
|------|-------------|----------|
| `market` | Execute at current price | Normal trades |
| `limit` | Execute at specified price or better | Price-sensitive |
| `stop` | Execute when price reaches trigger | Risk management |

## Amount Types

| Type | Description |
|------|-------------|
| `value` | Dollar amount to buy/sell |
| `units` | Number of units |
| `percentage` | Percentage of holding (sell) |
| `target_weight` | Rebalance to target % |

## Approval Thresholds

| Condition | Approval Required |
|-----------|-------------------|
| Trade > $5,000 | Adviser supervisor |
| Trade > $50,000 | Investment committee |
| New security | Product approval |
| Concentration > 10% | Risk review |
| No advice reference | Compliance review |

## Compliance Notes

- All trades logged with full audit trail
- Advice reference required for material trades
- Best execution policy applied
- Trade confirmations sent to client
- Records retained for 7 years
