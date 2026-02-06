---
name: slack-search
description: Search Slack messages and return message references. Requires user token (bot tokens cannot search).
composition:
  inputs:
    - search-query
  outputs:
    - message-refs
auth:
  env:
    - SLACK_USER_TOKEN
---

# slack-search

Search Slack workspace for messages matching a query. Returns message references (channel, timestamp, permalink) that can be passed to `slack-read` for full content retrieval.

## Why User Token Required

Slack's `search.messages` API requires a user token (`xoxp-*`). Bot tokens (`xoxb-*`) cannot search - this is a Slack platform limitation.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Slack search query (supports Slack search syntax) |
| limit | int | No | Max results (default: 20, max: 100) |
| json | flag | No | Output as JSON |

## Running

```bash
# Basic search
python scripts/run.py --query "deployment error"

# With limit
python scripts/run.py --query "from:@alice in:#engineering" --limit 50

# JSON output for piping to slack-read
python scripts/run.py --query "budget Q4" --json
```

## Output Format

Returns `message-refs` - a list of message references:

```json
{
  "query": "deployment error",
  "total": 42,
  "messages": [
    {
      "channel_id": "C01234567",
      "channel_name": "engineering",
      "ts": "1704067200.123456",
      "permalink": "https://workspace.slack.com/archives/C01234567/p1704067200123456",
      "user_id": "U01234567",
      "username": "alice",
      "snippet": "The deployment error was caused by..."
    }
  ]
}
```

## Composition

**Consumes:** `search-query`
**Produces:** `message-refs`
**Chains to:** `slack-read`
