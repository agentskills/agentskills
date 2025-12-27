---
name: portfolio-analyse
description: Comprehensive portfolio analysis including performance attribution, risk metrics, cost analysis, and rebalancing recommendations.
level: 2
operation: READ
license: Apache-2.0
domain: financial-advisory
composes:
  - portfolio-read
  - client-data-read
---

# Portfolio Analyse

Comprehensive portfolio analysis for review and optimisation.

## When to Use

Use this skill when:
- Preparing for client reviews
- Assessing portfolio health
- Identifying rebalancing opportunities
- Evaluating manager/fund performance
- Tax planning analysis

## Workflow Steps

```
1. RETRIEVE: Get portfolio and client data
       │
       ├── Current holdings and values
       ├── Historical valuations
       ├── Transaction history
       ├── Risk profile and targets
       └── Benchmark definitions
       │
       ▼
2. PERFORMANCE: Calculate return metrics
       │
       ├── Time-weighted returns (TWR)
       ├── Money-weighted returns (MWR)
       ├── Benchmark comparison
       └── Peer ranking
       │
       ▼
3. ATTRIBUTION: Explain performance sources
       │
       ├── Asset allocation effect
       ├── Security selection effect
       ├── Timing effect
       └── Currency effect (if applicable)
       │
       ▼
4. RISK: Assess risk metrics
       │
       ├── Volatility (standard deviation)
       ├── Maximum drawdown
       ├── Sharpe ratio
       ├── Tracking error
       └── Concentration analysis
       │
       ▼
5. COST: Analyse portfolio costs
       │
       ├── Management fees (MER/ICR)
       ├── Transaction costs
       ├── Platform fees
       ├── Adviser fees
       └── Total cost ratio
       │
       ▼
6. ALLOCATION: Check alignment
       │
       ├── Current vs target allocation
       ├── Drift analysis
       ├── Rebalancing recommendations
       └── Tax implications of rebalance
       │
       ▼
7. HOLDINGS: Individual security review
       │
       ├── Quality assessment
       ├── Concentration flags
       ├── ESG considerations
       └── Replacement candidates
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `period` | string | No | Analysis period: 1m, 3m, 6m, 1y, 3y, 5y, inception |
| `benchmark` | string | No | Benchmark for comparison |
| `include_tax` | boolean | No | Include tax analysis (default: false) |
| `include_esg` | boolean | No | Include ESG metrics (default: false) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `summary` | object | Executive summary |
| `performance` | object | Return metrics and attribution |
| `risk` | object | Risk metrics |
| `costs` | object | Fee and cost analysis |
| `allocation` | object | Asset allocation analysis |
| `holdings` | object[] | Individual holding analysis |
| `recommendations` | object[] | Action recommendations |
| `tax` | object | Tax considerations (if requested) |

## Usage

```
Analyse portfolio performance for client C-12345 over 1 year
```

```
Run full portfolio review for the Henderson family including tax implications
```

```
Check allocation drift and rebalancing needs for all growth-profile clients
```

## Example Response

```json
{
  "summary": {
    "total_value": 524000,
    "period_return": 12.5,
    "benchmark_return": 11.2,
    "excess_return": 1.3,
    "risk_adjusted_return": "Above average",
    "rebalance_required": true,
    "key_findings": [
      "Strong outperformance driven by overweight Australian equities",
      "International allocation has drifted 3% below target",
      "Two holdings flagged for quality concerns"
    ]
  },
  "performance": {
    "returns": {
      "1m": 2.1,
      "3m": 5.8,
      "6m": 8.2,
      "1y": 12.5,
      "3y_annualised": 8.4,
      "since_inception": 45.2,
      "inception_annualised": 7.8
    },
    "attribution": {
      "asset_allocation": 0.8,
      "security_selection": 0.4,
      "timing": 0.1,
      "total_active_return": 1.3
    },
    "benchmark_comparison": {
      "benchmark": "60/40 Growth Index",
      "tracking_error": 2.3,
      "information_ratio": 0.57
    }
  },
  "risk": {
    "volatility": 11.2,
    "max_drawdown": -8.5,
    "max_drawdown_date": "2024-04-15",
    "recovery_days": 45,
    "sharpe_ratio": 0.89,
    "sortino_ratio": 1.12,
    "beta": 0.95,
    "concentration": {
      "top_10_weight": 42,
      "single_stock_max": 8.5,
      "sector_max": 28
    }
  },
  "costs": {
    "total_cost_ratio": 0.82,
    "breakdown": {
      "investment_fees": 0.52,
      "platform_fees": 0.15,
      "adviser_fees": 0.15,
      "transaction_costs": 0.08
    },
    "annual_cost_dollars": 4297,
    "cost_vs_benchmark": "Below median"
  },
  "allocation": {
    "current": {
      "australian_equities": 38,
      "international_equities": 27,
      "property": 10,
      "fixed_income": 17,
      "cash": 8
    },
    "target": {
      "australian_equities": 35,
      "international_equities": 30,
      "property": 10,
      "fixed_income": 17,
      "cash": 8
    },
    "drift": {
      "australian_equities": 3,
      "international_equities": -3
    },
    "rebalance_recommended": true,
    "rebalance_trades": [
      {
        "action": "reduce",
        "asset_class": "australian_equities",
        "amount": 15720
      },
      {
        "action": "increase",
        "asset_class": "international_equities",
        "amount": 15720
      }
    ]
  },
  "holdings_flagged": [
    {
      "security": "XYZ Fund",
      "concern": "Underperformance vs peers (bottom quartile 3 years)",
      "recommendation": "Review for replacement"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "action": "Rebalance to target allocation",
      "rationale": "International equities 3% underweight"
    },
    {
      "priority": "medium",
      "action": "Review XYZ Fund",
      "rationale": "Persistent underperformance"
    }
  ]
}
```

## Analysis Thresholds

| Metric | Green | Amber | Red |
|--------|-------|-------|-----|
| Allocation drift | <2% | 2-5% | >5% |
| Vs benchmark | >-1% | -1% to -3% | <-3% |
| Single holding | <8% | 8-12% | >12% |
| Cost ratio | <1% | 1-1.5% | >1.5% |
| Sharpe ratio | >0.8 | 0.5-0.8 | <0.5 |

## Notes

- Performance calculated net of all fees
- Benchmark must align with risk profile
- Tax analysis requires cost base data
- ESG scores from third-party providers
- Historical data minimum 3 months for meaningful analysis
