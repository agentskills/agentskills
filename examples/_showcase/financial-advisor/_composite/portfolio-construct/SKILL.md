---
name: portfolio-construct
description: Construct an investment portfolio following the five-phase process from objectives to security selection. Produces implementable portfolio with trade list.
level: 2
operation: WRITE
license: Apache-2.0
domain: financial-advisory
composes:
  - client-data-read
  - portfolio-read
  - risk-profile-assess
  - compliance-check
---

# Portfolio Construct

Construct investment portfolio from objectives through to implementation.

## When to Use

Use this skill when:
- Building portfolio for new client
- Restructuring existing portfolio
- Implementing advice recommendations
- Transitioning from another adviser/platform

## Workflow Steps

```
1. EVALUATE: Assess current situation
       │
       ├── Existing holdings and values
       ├── Cost base and tax position
       ├── Unrealised gains/losses
       └── Transition constraints
       │
       ▼
2. OBJECTIVES: Determine investment objectives
       │
       ├── Return requirements
       ├── Income needs
       ├── Time horizon
       ├── Liquidity requirements
       └── Specific constraints (ESG, ethical)
       │
       ▼
3. ALLOCATION: Establish asset allocation
       │
       ├── Risk profile alignment
       ├── Strategic asset allocation (SAA)
       ├── Tactical tilts (if applicable)
       └── Rebalancing bands
       │
       ▼
4. SELECT: Choose specific investments
       │
       ├── Core holdings (passive/index)
       ├── Satellite holdings (active/thematic)
       ├── Product due diligence
       └── APL compliance check
       │
       ▼
5. IMPLEMENT: Generate trade list
       │
       ├── Transition strategy
       ├── Tax-efficient sequencing
       ├── Transaction cost optimisation
       └── Implementation timeline
```

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Client identifier |
| `account_id` | string | Yes | Account to construct portfolio in |
| `amount` | number | No | Investment amount (or use existing holdings) |
| `objectives` | object | No | Override client objectives |
| `constraints` | object | No | Special constraints (ESG, SRI, exclusions) |
| `model_portfolio` | string | No | Base model portfolio to use |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `portfolio` | object | Constructed portfolio specification |
| `allocation` | object | Asset allocation with targets |
| `holdings` | object[] | Specific securities selected |
| `implementation` | object | Trade list and timeline |
| `projections` | object | Expected return/risk characteristics |
| `compliance` | object | Compliance verification results |

## Usage

```
Construct growth portfolio for client C-12345 with $200,000
```

```
Restructure Mary Jones's portfolio to align with balanced risk profile
```

```
Build ESG-focused portfolio for new client, excluding fossil fuels
```

## Example Response

```json
{
  "portfolio": {
    "client_id": "C-12345",
    "account_id": "ACC-001",
    "name": "Growth Portfolio",
    "construction_date": "2024-12-23",
    "total_value": 200000,
    "risk_profile": "growth"
  },
  "allocation": {
    "strategic": {
      "australian_equities": {"target": 35, "range": [32, 38]},
      "international_equities": {"target": 30, "range": [27, 33]},
      "property": {"target": 10, "range": [8, 12]},
      "fixed_income": {"target": 17, "range": [14, 20]},
      "cash": {"target": 8, "range": [5, 12]}
    },
    "rationale": "Aligned with Growth risk profile, 10+ year horizon"
  },
  "holdings": [
    {
      "asset_class": "australian_equities",
      "allocation": 35,
      "value": 70000,
      "securities": [
        {
          "security_id": "VAS.ASX",
          "name": "Vanguard Australian Shares ETF",
          "type": "core",
          "weight": 25,
          "value": 50000,
          "rationale": "Low-cost broad market exposure"
        },
        {
          "security_id": "VHY.ASX",
          "name": "Vanguard High Yield ETF",
          "type": "satellite",
          "weight": 10,
          "value": 20000,
          "rationale": "Income focus, dividend tilt"
        }
      ]
    },
    {
      "asset_class": "international_equities",
      "allocation": 30,
      "value": 60000,
      "securities": [
        {
          "security_id": "VGS.ASX",
          "name": "Vanguard MSCI Index International",
          "type": "core",
          "weight": 20,
          "value": 40000,
          "rationale": "Developed markets exposure, hedged"
        },
        {
          "security_id": "VGE.ASX",
          "name": "Vanguard FTSE Emerging Markets",
          "type": "satellite",
          "weight": 10,
          "value": 20000,
          "rationale": "Emerging markets diversification"
        }
      ]
    },
    {
      "asset_class": "property",
      "allocation": 10,
      "value": 20000,
      "securities": [
        {
          "security_id": "VAP.ASX",
          "name": "Vanguard Australian Property",
          "type": "core",
          "weight": 10,
          "value": 20000,
          "rationale": "REIT exposure, income component"
        }
      ]
    },
    {
      "asset_class": "fixed_income",
      "allocation": 17,
      "value": 34000,
      "securities": [
        {
          "security_id": "VAF.ASX",
          "name": "Vanguard Australian Fixed Interest",
          "type": "core",
          "weight": 17,
          "value": 34000,
          "rationale": "Defensive allocation, duration management"
        }
      ]
    },
    {
      "asset_class": "cash",
      "allocation": 8,
      "value": 16000,
      "securities": [
        {
          "security_id": "CASH",
          "name": "Platform Cash Account",
          "type": "core",
          "weight": 8,
          "value": 16000,
          "rationale": "Liquidity, rebalancing reserve"
        }
      ]
    }
  ],
  "implementation": {
    "strategy": "immediate",
    "trades": [
      {"action": "buy", "security": "VAS.ASX", "value": 50000},
      {"action": "buy", "security": "VHY.ASX", "value": 20000},
      {"action": "buy", "security": "VGS.ASX", "value": 40000},
      {"action": "buy", "security": "VGE.ASX", "value": 20000},
      {"action": "buy", "security": "VAP.ASX", "value": 20000},
      {"action": "buy", "security": "VAF.ASX", "value": 34000}
    ],
    "estimated_costs": {
      "brokerage": 59.70,
      "spread_cost": 100,
      "total": 159.70
    },
    "settlement_date": "2024-12-27"
  },
  "projections": {
    "expected_return": 7.5,
    "expected_volatility": 11.2,
    "income_yield": 3.2,
    "franking_benefit": 0.4
  },
  "compliance": {
    "apl_check": "pass",
    "risk_alignment": "pass",
    "concentration_limits": "pass",
    "approved": true
  }
}
```

## Core/Satellite Framework

| Component | Allocation | Objective |
|-----------|------------|-----------|
| Core (70-80%) | Index/passive | Market return, low cost |
| Satellite (20-30%) | Active/thematic | Alpha generation, tilts |

## Investment Selection Criteria

| Criterion | Weight | Assessment |
|-----------|--------|------------|
| Fees (MER/ICR) | 25% | Lower is better |
| Tracking error | 20% | For index funds |
| Performance | 20% | vs benchmark and peers |
| Provider quality | 15% | Reputation, scale |
| Liquidity | 10% | Trading volume, spreads |
| Structure | 10% | Tax efficiency, domicile |

## Notes

- All securities must be on Approved Product List (APL)
- Tax implications modelled for transitions
- Model portfolios provide starting templates
- Customisation available within guidelines
- Rebalancing triggers set at construction
