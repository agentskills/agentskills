# holdings-ingest

Ingest and normalise portfolio holdings from various sources.

```yaml
name: holdings-ingest
version: 1.0.0
level: 1
category: portfolio-understanding
operation: READ

description: >
  Parse portfolio holdings from CSV, brokerage exports, or API feeds.
  Normalises to standard schema with security identifiers, quantities,
  cost basis, and acquisition dates.

tools:
  preferred:
    - name: portfolio_api
      operations: [fetch_holdings]
    - name: file_parser
      operations: [parse_csv, parse_xlsx]
  fallback:
    - name: mcp__filesystem
      operations: [read_file]
```

## Input Schema

```yaml
input:
  source_type:
    type: enum
    values: [csv, xlsx, api, manual]
    required: true

  source_location:
    type: string
    description: File path or API endpoint
    required: true

  brokerage:
    type: enum
    values: [interactive_brokers, schwab, fidelity, commsec, selfwealth, generic]
    description: Source format hint for parsing

  base_currency:
    type: string
    default: AUD
    description: Portfolio base currency for aggregation

  as_of_date:
    type: date
    description: Valuation date (defaults to today)
```

## Output Schema

```yaml
output:
  portfolio_id:
    type: string
    description: Generated or provided portfolio identifier

  as_of_date:
    type: date

  base_currency:
    type: string

  holdings:
    type: array
    items:
      security_id:
        type: string
        description: Normalised identifier (ISIN preferred)

      ticker:
        type: string
        description: Exchange ticker symbol

      name:
        type: string
        description: Security name

      asset_class:
        type: enum
        values: [equity, fixed_income, cash, alternative, commodity, real_estate, crypto]

      quantity:
        type: number
        description: Number of units held

      cost_basis:
        type: number
        description: Total cost basis in base currency

      cost_per_unit:
        type: number

      acquisition_date:
        type: date
        description: Original purchase date (for CGT)

      currency:
        type: string
        description: Security's trading currency

      exchange:
        type: string
        description: Primary exchange

      account:
        type: string
        description: Account/wrapper (taxable, super, ISA)

  parse_warnings:
    type: array
    description: Any data quality issues encountered

  unmatched_securities:
    type: array
    description: Securities that couldn't be identified
```

## Normalisation Rules

1. **Security Identification Priority**:
   - ISIN (preferred, globally unique)
   - CUSIP/SEDOL (regional)
   - Ticker + Exchange (fallback)

2. **Currency Handling**:
   - All values stored in original currency
   - FX rates fetched for base currency conversion
   - Conversion rate and date recorded

3. **Cost Basis**:
   - Prefer specific lot identification
   - Fall back to average cost if lots unavailable
   - Flag if cost basis missing (requires user input)

4. **Asset Classification**:
   - Auto-classify based on security type
   - Override available via mapping table

## Brokerage-Specific Parsing

```yaml
format_mappings:
  interactive_brokers:
    quantity_column: Position
    cost_column: Cost Basis
    date_format: YYYY-MM-DD

  commsec:
    quantity_column: Units
    cost_column: Purchase Price
    date_format: DD/MM/YYYY

  selfwealth:
    quantity_column: Quantity
    cost_column: Average Cost
    date_format: DD/MM/YYYY
```

## Example Usage

```yaml
# Ingest from CommSec export
input:
  source_type: csv
  source_location: /imports/commsec_holdings_2024.csv
  brokerage: commsec
  base_currency: AUD

# Output
output:
  portfolio_id: "pf_abc123"
  as_of_date: "2024-12-20"
  base_currency: "AUD"
  holdings:
    - security_id: "AU000000CBA7"
      ticker: "CBA.AX"
      name: "Commonwealth Bank of Australia"
      asset_class: "equity"
      quantity: 150
      cost_basis: 15750.00
      cost_per_unit: 105.00
      acquisition_date: "2022-03-15"
      currency: "AUD"
      exchange: "ASX"
      account: "taxable"
  parse_warnings: []
  unmatched_securities: []
```

## Error Handling

| Error | Recovery |
|-------|----------|
| File not found | Return error, suggest path check |
| Parse failure | Return partial with warnings |
| Unknown security | Add to unmatched_securities, continue |
| Missing cost basis | Flag for manual entry, use 0 |
| Currency mismatch | Fetch FX rate, log conversion |
