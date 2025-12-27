# Portfolio Manager Showcase

Comprehensive skill library for end-to-end portfolio management operations. Unlike simple Q&A interfaces, these skills enable agents to **take action** on portfolios—from ingestion through rebalancing to reporting.

## Design Philosophy

This showcase answers: "What can the user ask the portfolio manager to **do**, not just what questions they can ask?"

Each skill is designed for:
- **Actionable outcomes** (trade lists, not just analysis)
- **Constraint awareness** (respects IPS, tax rules, ESG filters)
- **Explainability** (every recommendation includes rationale)
- **Composability** (L1 → L2 → L3 building blocks)

## Skill Categories

### 1. Portfolio Understanding & Diagnostics
| Skill | Level | Purpose |
|-------|-------|---------|
| `holdings-ingest` | L1 | Parse and normalise portfolio data |
| `market-data-fetch` | L1 | Retrieve prices, benchmarks, fundamentals |
| `portfolio-summarise` | L2 | Breakdown by asset class, sector, geography, currency |
| `risk-profile-estimate` | L2 | Volatility, drawdown, concentration, factor exposures |
| `scenario-analyse` | L2 | Behaviour under rate hikes, recession, inflation |
| `benchmark-compare` | L2 | Highlight differences vs model/index |

### 2. Goal & Risk Alignment
| Skill | Level | Purpose |
|-------|-------|---------|
| `suitability-assess` | L2 | Check alignment with goals, horizon, risk tolerance |
| `goal-allocation-generate` | L2 | Target allocations mapped to specific goals |
| `efficient-frontier-analyse` | L2 | Risk/return trade-offs for alternatives |

### 3. Portfolio Construction & Rebalancing
| Skill | Level | Purpose |
|-------|-------|---------|
| `model-portfolio-propose` | L2 | Generate portfolio given constraints |
| `trade-list-generate` | L2 | Buy/sell to reach target with tax/cost optimisation |
| `rebalance-plan-create` | L2 | Bands, thresholds, calendar rules |
| `glidepath-design` | L2 | De-risking schedule toward target date |

### 4. Monitoring, Alerts & What-If
| Skill | Level | Purpose |
|-------|-------|---------|
| `drift-monitor` | L2 | Alert on weight/concentration/loss breaches |
| `whatif-simulate` | L2 | Impact of adding/removing positions |
| `performance-attribute` | L2 | Explain drivers of returns |

### 5. Custom Investment Recommendations
| Skill | Level | Purpose |
|-------|-------|---------|
| `fund-fit-score` | L2 | Score candidates for portfolio fit |
| `tax-implementation-suggest` | L2 | ETF vs fund, local vs offshore options |
| `position-rationale-generate` | L2 | Thesis, risks, exit criteria per position |

### 6. Cash Flows, Tax & Planning
| Skill | Level | Purpose |
|-------|-------|---------|
| `withdrawal-plan` | L2 | Schedule withdrawals with tax optimisation |
| `contribution-allocate` | L2 | Optimally deploy new capital |
| `tax-impact-estimate` | L2 | CGT consequences and alternatives |

### 7. Policy, Preferences & Controls
| Skill | Level | Purpose |
|-------|-------|---------|
| `ips-define` | L2 | Create Investment Policy Statement |
| `constraint-validate` | L1 | Check trades against rules |
| `constraint-enforce` | L2 | Block non-compliant proposals |

### 8. Explanation & Transparency
| Skill | Level | Purpose |
|-------|-------|---------|
| `metrics-translate` | L2 | Technical → plain language |
| `recommendation-explain` | L2 | Justify vs staying the course |
| `health-report-generate` | L2 | One-page shareable summary |

### Workflow Skills (L3)
| Skill | Purpose |
|-------|---------|
| `portfolio-onboard` | Full ingestion → analysis → suitability workflow |
| `rebalance-execute` | Monitor → propose → approve → trade workflow |
| `goal-based-review` | Periodic goal progress and reallocation |
| `annual-portfolio-review` | Comprehensive yearly assessment |

## API Mapping

Skills map directly to high-level API endpoints:

```
analyze_portfolio     → portfolio-summarise + risk-profile-estimate
propose_allocation    → goal-allocation-generate + model-portfolio-propose
generate_trade_plan   → trade-list-generate
monitor_and_alert     → drift-monitor
simulate_scenarios    → scenario-analyse + whatif-simulate
generate_report       → health-report-generate
```

## Composition Example

```yaml
# L3 rebalance-execute composes:
rebalance-execute:
  steps:
    - drift-monitor          # L2: Detect threshold breach
    - portfolio-summarise    # L2: Current state
    - trade-list-generate    # L2: Proposed trades
    - tax-impact-estimate    # L2: CGT analysis
    - constraint-enforce     # L2: Validate against IPS
    - recommendation-explain # L2: Generate rationale
    # → Human approval gate
    - trade-execute          # L1: Execute approved trades
    - health-report-generate # L2: Confirmation report
```

## Constraint Awareness

All proposal skills respect:
- **IPS constraints**: Max position size, excluded sectors, ESG rules
- **Tax rules**: CGT discount eligibility, wash sale prevention
- **Liquidity needs**: Minimum cash buffer maintained
- **Concentration limits**: Single-name and sector caps

## Sources & References

Architecture informed by:
- Mean-Variance Portfolio Theory
- Goals-Based Wealth Management frameworks
- Australian tax and regulatory requirements
- Modern portfolio management best practices

See individual SKILL.md files for detailed specifications.
