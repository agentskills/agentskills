# alert-send

Send portfolio alerts and notifications to configured channels.

```yaml
name: alert-send
version: 1.0.0
level: 1
category: monitoring
operation: WRITE

description: >
  Dispatch portfolio alerts to users via configured notification
  channels. Supports email, SMS, push notifications, and webhook
  integrations.

tools:
  preferred:
    - name: notification_service
      operations: [send_email, send_sms, send_push, send_webhook]
  fallback:
    - name: mcp__gmail
      operations: [send_email]
    - name: mcp__slack
      operations: [send_message]
```

## Input Schema

```yaml
input:
  alert:
    type: object
    required: true
    properties:
      type:
        type: enum
        values:
          - drift_breach
          - concentration_breach
          - loss_threshold
          - rebalance_due
          - trade_executed
          - goal_milestone
          - market_event
          - custom
        required: true

      severity:
        type: enum
        values: [critical, warning, info]
        default: info

      title:
        type: string
        required: true
        description: Alert headline

      message:
        type: string
        required: true
        description: Detailed alert message

      data:
        type: object
        description: Structured data payload for the alert
        properties:
          security_id: string
          current_value: number
          threshold_value: number
          breach_amount: number
          recommendation: string

      action_required:
        type: boolean
        default: false

      action_url:
        type: string
        description: Deep link to take action

  channels:
    type: array
    description: Override default channels
    items:
      type: enum
      values: [email, sms, push, slack, webhook]

  recipients:
    type: array
    description: Override default recipients
    items:
      type: string

  schedule:
    type: object
    description: Delay or schedule alert
    properties:
      send_at:
        type: datetime
      quiet_hours:
        type: boolean
        default: true
        description: Respect user's quiet hours setting
```

## Output Schema

```yaml
output:
  alert_id:
    type: string
    description: Unique alert reference

  status:
    type: enum
    values: [sent, queued, failed, suppressed]

  delivery:
    type: array
    items:
      channel: string
      recipient: string
      status: enum [delivered, pending, failed]
      sent_at: datetime
      error: string

  suppression_reason:
    type: string
    description: Why alert was not sent (if suppressed)
```

## Alert Types

### Drift Breach
```yaml
alert:
  type: drift_breach
  severity: warning
  title: "Position drift alert: CBA.AX"
  message: "CBA.AX has drifted to 12.5% weight, exceeding your 10% limit by 2.5%"
  data:
    security_id: "CBA.AX"
    current_value: 12.5
    threshold_value: 10.0
    breach_amount: 2.5
    recommendation: "Consider rebalancing to reduce position"
  action_required: true
  action_url: "https://app.example.com/rebalance?security=CBA.AX"
```

### Loss Threshold
```yaml
alert:
  type: loss_threshold
  severity: critical
  title: "Portfolio loss alert"
  message: "Your portfolio has declined 8.5% this month, exceeding your 7% loss threshold"
  data:
    current_value: -8.5
    threshold_value: -7.0
    period: "1M"
  action_required: true
```

### Trade Executed
```yaml
alert:
  type: trade_executed
  severity: info
  title: "Trade confirmation: Bought VAS.AX"
  message: "Successfully purchased 108 units of VAS.AX at $92.45 ($9,984.60 total)"
  data:
    security_id: "VAS.AX"
    action: "buy"
    quantity: 108
    price: 92.45
    total: 9984.60
    order_id: "ORD-2024122015432"
  action_required: false
```

## Channel Configuration

```yaml
channel_config:
  email:
    from: "portfolio@example.com"
    template: "portfolio_alert"
    include_data: true

  sms:
    provider: "twilio"
    max_length: 160
    critical_only: true  # Only send critical via SMS

  push:
    service: "firebase"
    icon: "alert"
    sound: true

  slack:
    webhook_url: "${SLACK_WEBHOOK}"
    channel: "#portfolio-alerts"
    mention_on_critical: true

  webhook:
    url: "https://api.example.com/alerts"
    method: "POST"
    headers:
      Authorization: "Bearer ${API_KEY}"
```

## Alert Suppression Rules

```yaml
suppression:
  # Duplicate suppression
  duplicate_window: 3600  # Don't repeat same alert within 1 hour

  # Quiet hours
  quiet_hours:
    enabled: true
    start: "22:00"
    end: "07:00"
    timezone: "Australia/Sydney"
    override_for: [critical]  # Critical alerts bypass quiet hours

  # Severity routing
  severity_channels:
    critical: [email, sms, push, slack]
    warning: [email, push, slack]
    info: [email, slack]

  # Rate limiting
  rate_limit:
    max_per_hour: 10
    max_per_day: 50
```

## Example Usage

```yaml
# Send concentration breach alert
input:
  alert:
    type: concentration_breach
    severity: warning
    title: "Sector concentration alert: Financials"
    message: |
      Your Financials sector allocation has reached 32%, exceeding
      your 30% limit. Consider reducing exposure to manage risk.
    data:
      sector: "Financials"
      current_value: 32.0
      threshold_value: 30.0
      breach_amount: 2.0
      affected_holdings: ["CBA.AX", "NAB.AX", "WBC.AX", "ANZ.AX"]
    action_required: true
    action_url: "https://app.example.com/rebalance?sector=financials"

  channels: [email, push]

# Output
output:
  alert_id: "ALT-20241220-001"
  status: sent
  delivery:
    - channel: email
      recipient: "user@example.com"
      status: delivered
      sent_at: "2024-12-20T10:30:00+11:00"
    - channel: push
      recipient: "device_token_123"
      status: delivered
      sent_at: "2024-12-20T10:30:01+11:00"
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Channel unavailable | Try next channel, queue for retry |
| Rate limited | Queue with delay |
| Invalid recipient | Log error, skip recipient |
| Template error | Fall back to plain text |
| Webhook timeout | Retry with backoff |
