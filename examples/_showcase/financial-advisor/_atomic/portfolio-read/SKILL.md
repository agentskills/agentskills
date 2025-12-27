---
name: portfolio-read
description: Read client portfolio holdings, valuations, and performance data. Integrates with custodian platforms for real-time positions.
level: 1
operation: READ
license: Apache-2.0
domain: financial-advisory
tool_discovery:
  platform:
    prefer: [hub24-portfolio, netwealth-portfolio, praemium-portfolio, xplan-portfolio]
    fallback: manual-portfolio
---

# Portfolio Read

Retrieve client portfolio holdings and performance data.

## When to Use

Use this skill when:
- Preparing for client reviews
- Analysing portfolio for rebalancing
- Generating performance reports
- Checking asset allocation drift
- Verifying trade execution

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `account_ids` | string[] | No | Specific accounts (default: all) |
| `include_history` | boolean | No | Include historical valuations |
| `period` | string | No | History period: 1m, 3m, 6m, 1y, 3y, inception |
| `benchmark` | string | No | Benchmark for comparison |
| `as_of_date` | string | No | Valuation date (default: latest) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `client_id` | string | Client identifier |
| `valuation_date` | string | As-of date for values |
| `total_value` | number | Total portfolio value |
| `accounts` | object[] | Account-level breakdown |
| `holdings` | object[] | Individual holdings |
| `allocation` | object | Asset allocation summary |
| `performance` | object | Performance metrics |
| `cash_available` | number | Available cash balance |

## Holdings Schema

```json
{
  "holdings": [
    {
      "security_id": "VAS.ASX",
      "name": "Vanguard Australian Shares ETF",
      "asset_class": "australian_equities",
      "units": 500,
      "price": 95.50,
      "value": 47750,
      "cost_base": 42000,
      "unrealised_gain": 5750,
      "weight": 15.2,
      "target_weight": 15.0,
      "drift": 0.2
    }
  ]
}
```

## Allocation Summary

```json
{
  "allocation": {
    "australian_equities": {
      "current": 35.2,
      "target": 35.0,
      "drift": 0.2,
      "value": 110500
    },
    "international_equities": {
      "current": 28.5,
      "target": 30.0,
      "drift": -1.5,
      "value": 89500
    },
    "fixed_income": {
      "current": 20.3,
      "target": 20.0,
      "drift": 0.3,
      "value": 63750
    },
    "property": {
      "current": 10.0,
      "target": 10.0,
      "drift": 0.0,
      "value": 31400
    },
    "cash": {
      "current": 6.0,
      "target": 5.0,
      "drift": 1.0,
      "value": 18850
    }
  }
}
```

## Performance Metrics

```json
{
  "performance": {
    "period": "1y",
    "return": {
      "total": 12.5,
      "capital": 8.2,
      "income": 4.3
    },
    "benchmark_return": 11.8,
    "excess_return": 0.7,
    "volatility": 12.3,
    "sharpe_ratio": 0.85,
    "max_drawdown": -8.5,
    "since_inception": {
      "annualised_return": 9.2,
      "total_return": 45.6
    }
  }
}
```

## Usage

```
Get portfolio summary for client C-12345
```

```
Show 1-year performance vs benchmark for the Henderson family
```

```
Check asset allocation drift for all accounts
```

## Example Response

```json
{
  "client_id": "C-12345",
  "valuation_date": "2024-12-22",
  "total_value": 314000,
  "accounts": [
    {
      "account_id": "ACC-001",
      "type": "investment",
      "value": 120000
    },
    {
      "account_id": "ACC-002",
      "type": "superannuation",
      "value": 194000
    }
  ],
  "allocation": {
    "growth_assets": 65.2,
    "defensive_assets": 34.8
  },
  "performance": {
    "ytd": 8.5,
    "1y": 12.5,
    "3y_annualised": 7.2
  },
  "cash_available": 18850,
  "rebalance_required": false,
  "drift_status": "within_tolerance"
}
```

## Drift Thresholds

| Asset Class | Tolerance | Trigger Rebalance |
|-------------|-----------|-------------------|
| Growth assets | ±5% | Yes |
| Defensive assets | ±5% | Yes |
| Individual asset class | ±3% | Consider |
| Single holding | ±2% | Monitor |

## Notes

- Real-time pricing during market hours
- End-of-day valuations used for reporting
- Performance calculations net of fees
- Tax lot tracking for CGT optimisation
- Multi-currency portfolios converted to AUD
