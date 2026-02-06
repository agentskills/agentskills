---
name: slack-deep-search
description: Deep search Slack with full message retrieval and summarization. Composes slack-search → slack-read → slack-summarize.
composition:
  inputs:
    - search-query
  outputs:
    - search-summary
  chain:
    - slack-search
    - slack-read
    - slack-summarize
auth:
  env:
    - SLACK_USER_TOKEN
---

# slack-deep-search

A composed skill that performs deep Slack search:

1. **Search** (`slack-search`) - Find messages matching query
2. **Read** (`slack-read`) - Fetch full content in parallel (fan-out)
3. **Summarize** (`slack-summarize`) - Aggregate and analyze (fan-in)

This demonstrates **reliable composition** - the entire pipeline is deterministic Python code. No fuzzy LLM orchestration that varies between runs.

## Why Composed Skills?

| Approach | Reliability | Speed | Consistency |
|----------|-------------|-------|-------------|
| MCP tool calls + LLM glue | Variable | Slow (multiple LLM calls) | Different each run |
| Composed skill pipeline | High | Fast (parallel fetch) | Same every run |

The LLM is only needed at the end for natural language summarization - all data fetching and analysis is deterministic.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Slack search query |
| question | string | No | Question to answer about results |
| limit | int | No | Max messages to fetch (default: 20) |
| format | string | No | Output: "structured", "prompt", "both" |
| json | flag | No | Output as JSON |

## Running

```bash
# Basic deep search
python scripts/run.py --query "deployment issue"

# With a specific question
python scripts/run.py --query "budget Q4" --question "What was the final decision?"

# More results
python scripts/run.py --query "from:@alice" --limit 50

# Just structured data (no LLM prompt)
python scripts/run.py --query "project update" --format structured --json
```

## Pipeline Flow

```
┌─────────────┐     ┌────────────┐     ┌─────────────────┐
│ slack-search│────▶│ slack-read │────▶│ slack-summarize │
│             │     │  (fan-out) │     │    (fan-in)     │
│ query → refs│     │ refs → msgs│     │ msgs → summary  │
└─────────────┘     └────────────┘     └─────────────────┘
      │                   │                    │
      ▼                   ▼                    ▼
  message-refs      message-content     search-summary
```

## Composition Validation

```bash
# Verify the chain is valid
skills-ref compose ./slack-search ./slack-read
# ✓ slack-search → slack-read (message-refs)

skills-ref compose ./slack-read ./slack-summarize
# ✓ slack-read → slack-summarize (message-content)
```

## Output

Returns `search-summary` with:
- Structured metadata (channels, participants, timeline)
- Per-channel breakdown with key messages
- LLM prompt ready for final summarization
