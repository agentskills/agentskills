#!/usr/bin/env python3
"""
REAL Benchmark: Composed Skills vs MCP Tool Calls

Actually runs both approaches and measures real metrics.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


# =============================================================================
# Slack API utilities
# =============================================================================

def slack_api_call(method: str, token: str, params: dict[str, Any]) -> dict:
    """Make a Slack API call."""
    url = f"https://slack.com/api/{method}"

    query_parts = []
    for k, v in params.items():
        if v is not None:
            if k == "query":
                query_parts.append(f"{k}={quote(str(v))}")
            else:
                query_parts.append(f"{k}={v}")
    if query_parts:
        url = f"{url}?{'&'.join(query_parts)}"

    request = Request(url)
    request.add_header("Authorization", f"Bearer {token}")

    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


# =============================================================================
# Claude API for MCP simulation
# =============================================================================

def claude_api_call(messages: list, tools: list, api_key: str) -> dict:
    """Call Claude API with tools."""
    url = "https://api.anthropic.com/v1/messages"

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "tools": tools,
        "messages": messages,
    }

    data = json.dumps(payload).encode()
    request = Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("x-api-key", api_key)
    request.add_header("anthropic-version", "2023-06-01")

    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


# =============================================================================
# Approach 1: Composed Pipeline (deterministic Python)
# =============================================================================

async def fetch_message_async(token: str, channel: str, ts: str, sem: asyncio.Semaphore) -> dict | None:
    """Fetch single message with semaphore."""
    async with sem:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: slack_api_call(
                    "conversations.history", token,
                    {"channel": channel, "latest": ts, "inclusive": "true", "limit": 1}
                )
            )
            if result.get("ok"):
                msgs = result.get("messages", [])
                if msgs:
                    return {"channel": channel, "ts": ts, "text": msgs[0].get("text", "")}
            return None
        except Exception:
            return None


def run_composed_pipeline(slack_token: str, query: str, limit: int) -> dict:
    """Run our composed pipeline and measure everything."""
    metrics = {
        "approach": "Composed Pipeline",
        "api_calls": 0,
        "llm_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "timings": {},
    }

    total_start = time.perf_counter()

    # Stage 1: Search
    search_start = time.perf_counter()
    search_result = slack_api_call("search.messages", slack_token, {"query": query, "count": limit})
    metrics["api_calls"] += 1
    metrics["timings"]["search_ms"] = (time.perf_counter() - search_start) * 1000

    matches = search_result.get("messages", {}).get("matches", [])
    refs = [(m.get("channel", {}).get("id"), m.get("ts"), m.get("channel", {}).get("name", ""))
            for m in matches]

    # Stage 2: Parallel fetch
    fetch_start = time.perf_counter()
    sem = asyncio.Semaphore(10)

    async def fetch_all():
        tasks = [fetch_message_async(slack_token, ch, ts, sem) for ch, ts, _ in refs if ch and ts]
        return await asyncio.gather(*tasks)

    results = asyncio.run(fetch_all())
    messages = [r for r in results if r]
    metrics["api_calls"] += len(refs)
    metrics["timings"]["fetch_ms"] = (time.perf_counter() - fetch_start) * 1000

    # Stage 3: Analysis (pure Python)
    analysis_start = time.perf_counter()
    channels = set()
    for ch, ts, name in refs:
        channels.add(name)
    summary = {
        "total_messages": len(messages),
        "channels": list(channels),
    }
    metrics["timings"]["analysis_ms"] = (time.perf_counter() - analysis_start) * 1000

    metrics["timings"]["total_ms"] = (time.perf_counter() - total_start) * 1000
    metrics["messages_retrieved"] = len(messages)
    metrics["result_preview"] = summary

    return metrics


# =============================================================================
# Approach 2: MCP Tool Calls (real Claude API calls)
# =============================================================================

def run_mcp_approach(slack_token: str, claude_key: str, query: str, limit: int) -> dict:
    """Run MCP approach with real Claude API calls."""
    metrics = {
        "approach": "MCP Tool Calls",
        "api_calls": 0,
        "llm_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "timings": {},
    }

    # Define tools that simulate MCP
    tools = [
        {
            "name": "slack_search",
            "description": "Search Slack messages. Returns message references with channel_id and timestamp.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "slack_get_message",
            "description": "Get full message content by channel_id and timestamp.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string"},
                    "ts": {"type": "string"}
                },
                "required": ["channel_id", "ts"]
            }
        },
        {
            "name": "summarize_messages",
            "description": "Summarize a list of messages.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "messages": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["messages"]
            }
        }
    ]

    messages = []
    collected_messages = []

    total_start = time.perf_counter()

    # Initial prompt
    messages.append({
        "role": "user",
        "content": f"Search Slack for '{query}' (limit {limit}), fetch the full content of each message found, then summarize them. Use the tools provided."
    })

    # Tool call loop
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        llm_start = time.perf_counter()

        try:
            response = claude_api_call(messages, tools, claude_key)
        except HTTPError as e:
            metrics["error"] = f"Claude API error: {e.code}"
            break

        metrics["llm_calls"] += 1
        metrics["input_tokens"] += response.get("usage", {}).get("input_tokens", 0)
        metrics["output_tokens"] += response.get("usage", {}).get("output_tokens", 0)
        metrics["timings"][f"llm_call_{iteration}_ms"] = (time.perf_counter() - llm_start) * 1000

        # Check stop reason
        stop_reason = response.get("stop_reason")
        content = response.get("content", [])

        # Add assistant response
        messages.append({"role": "assistant", "content": content})

        if stop_reason == "end_turn":
            # Done
            break

        if stop_reason == "tool_use":
            # Process tool calls
            tool_results = []

            for block in content:
                if block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    tool_input = block.get("input", {})
                    tool_id = block.get("id")

                    api_start = time.perf_counter()

                    if tool_name == "slack_search":
                        result = slack_api_call("search.messages", slack_token, {
                            "query": tool_input.get("query", query),
                            "count": tool_input.get("limit", limit)
                        })
                        metrics["api_calls"] += 1

                        matches = result.get("messages", {}).get("matches", [])
                        tool_result = {
                            "total": result.get("messages", {}).get("total", 0),
                            "messages": [
                                {"channel_id": m.get("channel", {}).get("id"),
                                 "ts": m.get("ts"),
                                 "channel_name": m.get("channel", {}).get("name"),
                                 "snippet": m.get("text", "")[:100]}
                                for m in matches[:limit]
                            ]
                        }

                    elif tool_name == "slack_get_message":
                        try:
                            result = slack_api_call("conversations.history", slack_token, {
                                "channel": tool_input.get("channel_id"),
                                "latest": tool_input.get("ts"),
                                "inclusive": "true",
                                "limit": 1
                            })
                            metrics["api_calls"] += 1

                            msgs = result.get("messages", [])
                            if msgs and result.get("ok"):
                                msg = msgs[0]
                                tool_result = {
                                    "channel_id": tool_input.get("channel_id"),
                                    "text": msg.get("text", ""),
                                    "user": msg.get("user", ""),
                                    "ts": tool_input.get("ts")
                                }
                                collected_messages.append(tool_result)
                            else:
                                tool_result = {"error": "Message not found"}
                        except Exception as e:
                            tool_result = {"error": str(e)}
                            metrics["api_calls"] += 1

                    elif tool_name == "summarize_messages":
                        # This would normally be done by Claude, just return ack
                        tool_result = {"status": "summarized", "count": len(tool_input.get("messages", []))}

                    else:
                        tool_result = {"error": f"Unknown tool: {tool_name}"}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(tool_result)
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    metrics["timings"]["total_ms"] = (time.perf_counter() - total_start) * 1000
    metrics["messages_retrieved"] = len(collected_messages)
    metrics["iterations"] = iteration

    return metrics


# =============================================================================
# Main
# =============================================================================

def main():
    slack_token = os.environ.get("SLACK_USER_TOKEN")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")

    if not slack_token:
        print("Error: SLACK_USER_TOKEN required", file=sys.stderr)
        sys.exit(1)
    if not claude_key:
        print("Error: ANTHROPIC_API_KEY required", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1] if len(sys.argv) > 1 else "test"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5  # Keep small for cost

    print(f"REAL BENCHMARK: query='{query}', limit={limit}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # Run composed pipeline
    print("\n[1/2] Running Composed Pipeline...")
    composed = run_composed_pipeline(slack_token, query, limit)
    print(f"      Done in {composed['timings']['total_ms']:.0f}ms")

    # Run MCP approach
    print("\n[2/2] Running MCP Tool Calls (real Claude API)...")
    mcp = run_mcp_approach(slack_token, claude_key, query, limit)
    print(f"      Done in {mcp['timings']['total_ms']:.0f}ms")

    # Results
    print("\n" + "=" * 70)
    print("RESULTS (measured, not estimated)")
    print("=" * 70)

    print(f"\n{'Metric':<25} {'Composed':<20} {'MCP':<20}")
    print("-" * 65)
    print(f"{'Total time (ms)':<25} {composed['timings']['total_ms']:<20.0f} {mcp['timings']['total_ms']:<20.0f}")
    print(f"{'Slack API calls':<25} {composed['api_calls']:<20} {mcp['api_calls']:<20}")
    print(f"{'LLM calls':<25} {composed['llm_calls']:<20} {mcp['llm_calls']:<20}")
    print(f"{'Input tokens':<25} {composed['input_tokens']:<20} {mcp['input_tokens']:<20}")
    print(f"{'Output tokens':<25} {composed['output_tokens']:<20} {mcp['output_tokens']:<20}")
    print(f"{'Messages retrieved':<25} {composed['messages_retrieved']:<20} {mcp['messages_retrieved']:<20}")

    total_tokens_mcp = mcp['input_tokens'] + mcp['output_tokens']

    print("\n" + "-" * 65)
    print("SUMMARY")
    print("-" * 65)
    print(f"Speed improvement: {mcp['timings']['total_ms'] / composed['timings']['total_ms']:.1f}x faster")
    print(f"Token savings: {total_tokens_mcp:,} tokens (100% - composed uses 0)")
    print(f"API calls: {composed['api_calls']} vs {mcp['api_calls']}")

    # Cost estimate (Claude Sonnet pricing: $3/M input, $15/M output)
    input_cost = mcp['input_tokens'] * 3 / 1_000_000
    output_cost = mcp['output_tokens'] * 15 / 1_000_000
    total_cost = input_cost + output_cost
    print(f"MCP cost estimate: ${total_cost:.4f} per query")
    print(f"Composed cost: $0.00 (no LLM orchestration)")

    print("\n" + "=" * 70)
    print("RAW METRICS")
    print("=" * 70)
    print("\nComposed Pipeline:")
    print(json.dumps(composed, indent=2))
    print("\nMCP Tool Calls:")
    print(json.dumps(mcp, indent=2))


if __name__ == "__main__":
    main()
