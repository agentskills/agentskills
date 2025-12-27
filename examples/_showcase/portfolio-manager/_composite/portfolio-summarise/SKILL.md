# portfolio-summarise

Ingest and summarise portfolio by asset class, sector, geography, and currency.

```yaml
name: portfolio-summarise
version: 1.0.0
level: 2
category: portfolio-understanding
operation: READ

description: >
  Create a comprehensive breakdown of current portfolio composition.
  Aggregates holdings into meaningful categories and provides
  context for portfolio analysis.

composes:
  - holdings-ingest
  - market-data-fetch

tools:
  preferred:
    - name: portfolio_analytics
      operations: [summarise]
```

## Input Schema

```yaml
input:
  portfolio_source:
    type: object
    description: Where to get holdings from
    properties:
      type: enum [file, api, provided]
      location: string  # File path or API endpoint
      holdings: array   # If type=provided

  include_benchmarks:
    type: boolean
    default: true
    description: Include benchmark comparison in summary

  groupings:
    type: array
    default: [asset_class, sector, geography, currency]
    items:
      type: enum
      values:
        - asset_class
        - sector
        - industry
        - geography
        - currency
        - account
        - market_cap
        - style
        - credit_rating
        - duration_bucket

  valuation_currency:
    type: string
    default: AUD
```

## Output Schema

```yaml
output:
  as_of_date:
    type: date

  portfolio_value:
    type: number
    description: Total portfolio value in valuation currency

  holdings_count:
    type: number

  # Breakdown by requested groupings
  breakdown:
    asset_class:
      type: array
      items:
        name: string
        value: number
        weight: number
        holdings_count: number
        holdings: array

    sector:
      type: array
      items:
        name: string
        value: number
        weight: number

    geography:
      type: array
      items:
        country: string
        region: string
        value: number
        weight: number

    currency:
      type: array
      items:
        currency: string
        value: number
        weight: number
        fx_exposure: number

  # Additional analytics
  diversification:
    herfindahl_index: number
    effective_positions: number
    largest_position:
      security: string
      weight: number
    top_10_weight: number

  liquidity_profile:
    highly_liquid: number      # % in large caps/ETFs
    moderately_liquid: number
    less_liquid: number

  income_characteristics:
    weighted_yield: number
    estimated_annual_income: number
    ex_div_next_30_days: array

  # Optional benchmark comparison
  benchmark_comparison:
    benchmark: string
    active_weights:
      overweight: array
      underweight: array
    tracking_difference: number
```

## Composition Flow

```yaml
steps:
  1_ingest:
    skill: holdings-ingest
    input:
      source_type: ${input.portfolio_source.type}
      source_location: ${input.portfolio_source.location}
    output: raw_holdings

  2_enrich:
    skill: market-data-fetch
    input:
      securities: ${raw_holdings.security_ids}
      data_types: [price, fundamentals]
    output: market_data

  3_classify:
    action: internal
    description: |
      Map each holding to classification attributes:
      - Asset class from security type
      - Sector/industry from fundamentals
      - Geography from domicile/listing
      - Currency from trading currency

  4_aggregate:
    action: internal
    description: |
      Group holdings by requested dimensions
      Calculate weights and totals

  5_analyse:
    action: internal
    description: |
      Calculate diversification metrics
      Assess liquidity profile
      Estimate income characteristics

  6_compare:
    condition: ${input.include_benchmarks}
    action: internal
    description: Calculate active weights vs benchmark
```

## Example Output

```yaml
output:
  as_of_date: "2024-12-20"
  portfolio_value: 500000
  holdings_count: 12

  breakdown:
    asset_class:
      - name: "Australian Equities"
        value: 200000
        weight: 40.0
        holdings_count: 5
      - name: "International Equities"
        value: 150000
        weight: 30.0
        holdings_count: 3
      - name: "Fixed Income"
        value: 100000
        weight: 20.0
        holdings_count: 2
      - name: "Cash"
        value: 50000
        weight: 10.0
        holdings_count: 2

    sector:
      - name: "Financials"
        value: 100000
        weight: 20.0
      - name: "Materials"
        value: 75000
        weight: 15.0
      - name: "Healthcare"
        value: 50000
        weight: 10.0
      # ...

    geography:
      - country: "Australia"
        region: "Asia Pacific"
        value: 250000
        weight: 50.0
      - country: "United States"
        region: "North America"
        value: 125000
        weight: 25.0
      # ...

    currency:
      - currency: "AUD"
        value: 300000
        weight: 60.0
        fx_exposure: 0  # No FX risk
      - currency: "USD"
        value: 150000
        weight: 30.0
        fx_exposure: 150000
      # ...

  diversification:
    herfindahl_index: 0.12
    effective_positions: 8.3
    largest_position:
      security: "VAS.AX"
      weight: 15.0
    top_10_weight: 85.0

  liquidity_profile:
    highly_liquid: 75.0
    moderately_liquid: 20.0
    less_liquid: 5.0

  income_characteristics:
    weighted_yield: 3.2
    estimated_annual_income: 16000
    ex_div_next_30_days:
      - security: "CBA.AX"
        ex_date: "2024-01-15"
        amount: 225

  benchmark_comparison:
    benchmark: "60/40 Portfolio"
    active_weights:
      overweight:
        - category: "Australian Equities"
          active: +10.0
        - category: "Financials"
          active: +5.0
      underweight:
        - category: "International Equities"
          active: -10.0
    tracking_difference: 0.5
```

## Visualisation Hints

```yaml
visualisation:
  pie_charts:
    - asset_class
    - sector
    - geography

  tables:
    - holdings_detail
    - currency_exposure

  comparisons:
    - benchmark_bar_chart
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Holdings ingestion fails | Return partial with errors |
| Market data unavailable | Use last known prices, flag stale |
| Unknown security classification | Add to "Unclassified" bucket |
| Currency conversion fails | Use base currency, warn |
