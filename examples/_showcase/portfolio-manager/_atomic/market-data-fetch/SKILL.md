# market-data-fetch

Retrieve market data including prices, benchmarks, and fundamentals.

```yaml
name: market-data-fetch
version: 1.0.0
level: 1
category: portfolio-understanding
operation: READ

description: >
  Fetch current and historical market data for securities, indices,
  and benchmarks. Supports prices, dividends, fundamentals, and
  reference data.

tools:
  preferred:
    - name: market_data_api
      operations: [get_quote, get_history, get_fundamentals]
  fallback:
    - name: yahoo_finance
      operations: [get_quote, get_history]
    - name: alpha_vantage
      operations: [get_quote, get_history]
```

## Input Schema

```yaml
input:
  securities:
    type: array
    items:
      type: string
    description: List of security identifiers (ISIN, ticker, or CUSIP)
    required: true

  data_types:
    type: array
    items:
      type: enum
      values: [price, history, dividends, fundamentals, splits, benchmark]
    default: [price]

  start_date:
    type: date
    description: Start date for historical data

  end_date:
    type: date
    description: End date for historical data (defaults to today)

  frequency:
    type: enum
    values: [daily, weekly, monthly]
    default: daily
    description: Frequency for historical data

  currency:
    type: string
    description: Convert prices to this currency
```

## Output Schema

```yaml
output:
  as_of:
    type: datetime
    description: Timestamp of data retrieval

  quotes:
    type: object
    description: Current prices keyed by security ID
    properties:
      "[security_id]":
        last_price: number
        bid: number
        ask: number
        volume: number
        change_pct: number
        currency: string
        exchange: string
        timestamp: datetime

  history:
    type: object
    description: Historical prices keyed by security ID
    properties:
      "[security_id]":
        type: array
        items:
          date: date
          open: number
          high: number
          low: number
          close: number
          adj_close: number
          volume: number

  dividends:
    type: object
    properties:
      "[security_id]":
        type: array
        items:
          ex_date: date
          pay_date: date
          amount: number
          currency: string
          type: enum [regular, special, return_of_capital]

  fundamentals:
    type: object
    properties:
      "[security_id]":
        market_cap: number
        pe_ratio: number
        pb_ratio: number
        dividend_yield: number
        eps: number
        revenue: number
        sector: string
        industry: string

  benchmarks:
    type: object
    description: Benchmark index data
    properties:
      "[benchmark_id]":
        name: string
        last_value: number
        ytd_return: number
        history: array

  errors:
    type: array
    description: Securities that couldn't be fetched
```

## Supported Benchmarks

```yaml
benchmarks:
  # Australian
  ASX200: "S&P/ASX 200"
  ASX300: "S&P/ASX 300"
  AXJO: "S&P/ASX 200 Accumulation"

  # US
  SPX: "S&P 500"
  NDX: "NASDAQ 100"
  DJI: "Dow Jones Industrial"

  # Global
  MSCI_WORLD: "MSCI World"
  MSCI_ACWI: "MSCI All Country World"
  MSCI_EM: "MSCI Emerging Markets"

  # Fixed Income
  AUBBF: "Bloomberg AusBond Composite"
  AGG: "Bloomberg US Aggregate"
```

## Caching Behaviour

```yaml
cache:
  quotes:
    ttl: 60  # 1 minute for real-time quotes
    stale_threshold: 300  # Warn if > 5 mins old

  history:
    ttl: 86400  # 24 hours for historical
    incremental: true  # Only fetch new data points

  fundamentals:
    ttl: 86400  # 24 hours

  benchmarks:
    ttl: 3600  # 1 hour
```

## Example Usage

```yaml
# Fetch current prices and 1-year history
input:
  securities:
    - "AU000000CBA7"  # CBA
    - "AU000000BHP4"  # BHP
    - "VAS.AX"        # Vanguard Australian Shares
  data_types: [price, history, fundamentals]
  start_date: "2023-12-20"
  end_date: "2024-12-20"
  currency: "AUD"

# Output (abbreviated)
output:
  as_of: "2024-12-20T10:30:00+11:00"
  quotes:
    AU000000CBA7:
      last_price: 142.50
      change_pct: 0.35
      currency: AUD
      volume: 2450000
  history:
    AU000000CBA7:
      - date: "2024-12-20"
        close: 142.50
        adj_close: 142.50
      # ... 252 trading days
  fundamentals:
    AU000000CBA7:
      market_cap: 268000000000
      pe_ratio: 21.5
      dividend_yield: 3.8
      sector: Financials
```

## Rate Limiting

```yaml
rate_limits:
  yahoo_finance:
    requests_per_minute: 60
    batch_size: 100

  alpha_vantage:
    requests_per_minute: 5
    requires_api_key: true

  refinitiv:
    requests_per_minute: 1000
    requires_subscription: true
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Security not found | Add to errors array, continue |
| Rate limited | Exponential backoff, retry 3x |
| Stale data | Return with warning flag |
| API unavailable | Try fallback provider |
| Invalid date range | Adjust to available range, warn |
