# trade-order-execute

Execute a single trade order through brokerage.

```yaml
name: trade-order-execute
version: 1.0.0
level: 1
category: portfolio-construction
operation: WRITE

description: >
  Submit a trade order to the connected brokerage or trading platform.
  Supports market, limit, and stop orders with pre-trade validation.

requires_approval: true
approval_context: "Trade execution requires explicit confirmation"

tools:
  preferred:
    - name: brokerage_api
      operations: [submit_order, check_status, cancel_order]
  fallback:
    - name: trading_platform
      operations: [execute_trade]
```

## Input Schema

```yaml
input:
  order:
    type: object
    required: true
    properties:
      security_id:
        type: string
        required: true
        description: Security to trade (ISIN, ticker)

      action:
        type: enum
        values: [buy, sell]
        required: true

      quantity:
        type: number
        description: Number of units (mutually exclusive with value)

      value:
        type: number
        description: Dollar amount to trade (mutually exclusive with quantity)

      order_type:
        type: enum
        values: [market, limit, stop, stop_limit]
        default: market

      limit_price:
        type: number
        description: Required for limit/stop_limit orders

      stop_price:
        type: number
        description: Required for stop/stop_limit orders

      time_in_force:
        type: enum
        values: [day, gtc, ioc, fok]
        default: day
        description: |
          day: Valid for trading day
          gtc: Good til cancelled
          ioc: Immediate or cancel
          fok: Fill or kill

      account:
        type: string
        description: Trading account if multiple

  validation:
    type: object
    properties:
      skip_constraint_check:
        type: boolean
        default: false
        description: Skip IPS constraint validation

      max_slippage_pct:
        type: number
        default: 0.5
        description: Maximum acceptable slippage from quote

      dry_run:
        type: boolean
        default: false
        description: Validate without executing
```

## Output Schema

```yaml
output:
  order_id:
    type: string
    description: Brokerage order reference

  status:
    type: enum
    values: [submitted, filled, partial, rejected, cancelled, pending]

  execution:
    type: object
    properties:
      filled_quantity:
        type: number
      average_price:
        type: number
      total_value:
        type: number
      commission:
        type: number
      fees:
        type: number
      net_amount:
        type: number
      execution_time:
        type: datetime
      venue:
        type: string

  validation_result:
    type: object
    properties:
      passed: boolean
      warnings: array
      constraint_check: object

  audit:
    type: object
    properties:
      submitted_at: datetime
      submitted_by: string
      approval_reference: string
      pre_trade_quote: number
      post_trade_price: number
      slippage_pct: number
```

## Pre-Trade Checks

```yaml
pre_trade_validation:
  # Always performed
  - security_tradeable: true
  - market_open: true
  - sufficient_funds: true  # For buys
  - sufficient_holdings: true  # For sells
  - order_size_valid: true

  # Configurable
  - constraint_check:
      enabled: true
      uses: constraint-validate
  - concentration_check:
      enabled: true
      max_position_pct: 10
  - liquidity_check:
      enabled: true
      max_adv_pct: 5  # Max % of average daily volume
```

## Order Types

### Market Order
```yaml
order:
  security_id: "CBA.AX"
  action: buy
  quantity: 100
  order_type: market
  time_in_force: day
```

### Limit Order
```yaml
order:
  security_id: "BHP.AX"
  action: sell
  quantity: 50
  order_type: limit
  limit_price: 45.50
  time_in_force: gtc
```

### Stop Loss
```yaml
order:
  security_id: "WOW.AX"
  action: sell
  quantity: 200
  order_type: stop
  stop_price: 32.00
  time_in_force: gtc
```

## Example Usage

```yaml
# Execute market buy order
input:
  order:
    security_id: "VAS.AX"
    action: buy
    value: 10000  # Buy $10,000 worth
    order_type: market
    time_in_force: day
    account: "taxable"
  validation:
    max_slippage_pct: 0.3

# Successful execution
output:
  order_id: "ORD-2024122015432"
  status: filled
  execution:
    filled_quantity: 108
    average_price: 92.45
    total_value: 9984.60
    commission: 9.95
    fees: 0.00
    net_amount: 9994.55
    execution_time: "2024-12-20T10:15:32+11:00"
    venue: "ASX"
  validation_result:
    passed: true
    warnings: []
    constraint_check:
      valid: true
      new_position_weight: 4.2
  audit:
    submitted_at: "2024-12-20T10:15:30+11:00"
    submitted_by: "agent"
    approval_reference: "APR-123456"
    pre_trade_quote: 92.40
    post_trade_price: 92.45
    slippage_pct: 0.05
```

## Order Rejection Reasons

| Reason | Description | Recovery |
|--------|-------------|----------|
| `insufficient_funds` | Not enough cash for buy | Reduce size or deposit |
| `insufficient_holdings` | Can't sell more than held | Check position |
| `market_closed` | Outside trading hours | Queue for next session |
| `security_halted` | Trading halt in effect | Wait for resumption |
| `constraint_violation` | IPS breach | Modify order or get override |
| `price_moved` | Limit price no longer valid | Update limit price |

## Audit Trail

Every execution creates immutable audit record:

```yaml
audit_record:
  order_id: string
  security: string
  action: string
  requested_quantity: number
  filled_quantity: number
  requested_price: number  # null for market
  filled_price: number
  timestamp: datetime
  user: string
  approval_ref: string
  constraint_check_result: object
  pre_trade_portfolio_state: snapshot
  post_trade_portfolio_state: snapshot
```

## Error Handling

| Error | Recovery |
|-------|----------|
| API timeout | Retry with exponential backoff |
| Order rejected | Return detailed rejection reason |
| Partial fill | Report filled/remaining, await |
| Network error | Check order status before retry |
| Invalid security | Validate security ID first |
