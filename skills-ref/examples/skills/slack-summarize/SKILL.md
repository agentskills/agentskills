---
name: slack-summarize
description: Summarize Slack messages with structured analysis. Provides both algorithmic summary and LLM prompt.
composition:
  inputs:
    - message-content
  outputs:
    - search-summary
---

# slack-summarize

Fan-in skill that takes multiple Slack messages and produces a structured summary. Provides:
1. **Algorithmic summary** - Statistics, timeline, participants, channels (no LLM needed)
2. **LLM prompt** - Pre-formatted context for natural language summarization

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| input | file/stdin | Yes | JSON message content from slack-read |
| question | string | No | Question to answer (included in LLM prompt) |
| format | string | No | Output format: "structured", "prompt", "both" (default: both) |
| json | flag | No | Output as JSON |

## Running

```bash
# Pipe from slack-read
python ../slack-read/scripts/run.py --input refs.json --json | python scripts/run.py

# With a question to answer
python scripts/run.py --input messages.json --question "What was decided about the budget?"

# Just the structured summary (no LLM prompt)
python scripts/run.py --input messages.json --format structured
```

## Output Format

Returns `search-summary` with structured analysis:

```json
{
  "meta": {
    "total_messages": 15,
    "channels": ["engineering", "general"],
    "participants": ["alice", "bob", "carol"],
    "date_range": {
      "earliest": "2024-01-01T09:00:00Z",
      "latest": "2024-01-15T17:30:00Z"
    }
  },
  "by_channel": {
    "engineering": {
      "count": 10,
      "participants": ["alice", "bob"],
      "key_messages": [...]
    }
  },
  "timeline": [
    {"date": "2024-01-01", "count": 5, "channels": ["engineering"]},
    {"date": "2024-01-15", "count": 10, "channels": ["engineering", "general"]}
  ],
  "llm_prompt": "Based on the following Slack messages..."
}
```

## Composition

**Consumes:** `message-content` (from slack-read)
**Produces:** `search-summary`
**End of chain** - produces final output
