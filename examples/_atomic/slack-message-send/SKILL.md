---
name: slack-message-send
description: Send a message to a Slack channel or user. Supports text, blocks, and attachments. Use for notifications, alerts, or team communication.
level: 1
operation: WRITE
license: Apache-2.0
---

# Slack Message Send

Send a message to a Slack channel or direct message to a user.

## When to Use

Use this skill when:
- Sending notifications to a team channel
- Alerting about important events
- Sharing updates or status reports
- Direct messaging a team member

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel` | string | Yes | Channel ID, channel name (#general), or user ID for DM |
| `text` | string | Yes | Message text (markdown supported) |
| `blocks` | object[] | No | Slack Block Kit blocks for rich formatting |
| `attachments` | object[] | No | Message attachments (legacy, prefer blocks) |
| `thread_ts` | string | No | Reply to a thread (message timestamp) |
| `unfurl_links` | boolean | No | Unfurl URLs in message (default: true) |
| `unfurl_media` | boolean | No | Unfurl media URLs (default: true) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Whether message was sent successfully |
| `channel` | string | Channel ID where message was posted |
| `ts` | string | Message timestamp (use for threading) |
| `message` | object | The posted message object |

## Usage

```
Send a Slack message to #engineering: "Deployment complete! :rocket: All services are healthy."
```

```
Send a DM to U1234567 saying "Your build has finished" in thread 1703012345.123456
```

## Example Response

```json
{
  "ok": true,
  "channel": "C1234567890",
  "ts": "1703012400.000100",
  "message": {
    "type": "message",
    "text": "Deployment complete! :rocket: All services are healthy.",
    "user": "U0987654321",
    "ts": "1703012400.000100"
  }
}
```

## Why This Matters for Composition

As a WRITE operation, `slack-message-send` enables notification in workflows:
- **deploy-notify** (Level 2) can run deployment + send status to Slack
- **on-call-alert** (Level 3) can escalate alerts with rich formatting

## Notes

- Requires Slack Bot token with appropriate scopes
- Channel names should include # prefix or use channel ID
- For rich formatting, use Slack Block Kit blocks
- Rate limits apply (typically 1 msg/sec per channel)
- Inspired by n8n's Slack node (Message resource, Send operation)
