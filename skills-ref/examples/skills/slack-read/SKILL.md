---
name: slack-read
description: Read full message content from Slack message references. Fetches in parallel for speed.
composition:
  inputs:
    - message-refs
  outputs:
    - message-content
auth:
  env:
    - SLACK_USER_TOKEN
    - SLACK_BOT_TOKEN
---

# slack-read

Fetch full message content from Slack given message references. Uses parallel fetching (fan-out) for speed. Includes thread context and rich metadata.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| input | file/stdin | Yes | JSON message refs from slack-search |
| include-threads | flag | No | Fetch thread replies (default: false) |
| max-parallel | int | No | Max concurrent requests (default: 10) |
| json | flag | No | Output as JSON |

## Running

```bash
# Pipe from slack-search
python ../slack-search/scripts/run.py --query "budget" --json | python scripts/run.py

# From file
python scripts/run.py --input refs.json

# Include thread context
python scripts/run.py --input refs.json --include-threads
```

## Output Format

Returns `message-content` - full messages with metadata:

```json
{
  "fetched": 15,
  "messages": [
    {
      "channel_id": "C01234567",
      "channel_name": "engineering",
      "ts": "1704067200.123456",
      "datetime": "2024-01-01T00:00:00Z",
      "user_id": "U01234567",
      "username": "alice",
      "text": "Full message text here...",
      "permalink": "https://...",
      "thread_ts": null,
      "reply_count": 0,
      "reactions": [{"name": "thumbsup", "count": 3}]
    }
  ]
}
```

## Composition

**Consumes:** `message-refs` (from slack-search)
**Produces:** `message-content`
**Chains to:** `slack-summarize`
