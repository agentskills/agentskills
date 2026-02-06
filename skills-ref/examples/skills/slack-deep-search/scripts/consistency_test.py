#!/usr/bin/env python3
"""
Consistency Test: Run both approaches 5 times and compare results.
All measurements are REAL - actual API calls, actual timing.
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
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode())


async def fetch_msg(token: str, ch: str, ts: str, sem: asyncio.Semaphore) -> dict | None:
    async with sem:
        loop = asyncio.get_event_loop()
        try:
            r = await loop.run_in_executor(None, lambda: slack_api_call(
                "conversations.history", token,
                {"channel": ch, "latest": ts, "inclusive": "true", "limit": 1}
            ))
            if r.get("ok") and r.get("messages"):
                return {"channel": ch, "ts": ts, "text": r["messages"][0].get("text", "")[:100]}
        except:
            pass
        return None


def run_composed(slack_token: str, query: str, limit: int) -> dict:
    """Run composed pipeline - REAL execution."""
    start = time.perf_counter()

    # Search
    search_result = slack_api_call("search.messages", slack_token, {"query": query, "count": limit})
    matches = search_result.get("messages", {}).get("matches", [])
    refs = [(m.get("channel", {}).get("id"), m.get("ts")) for m in matches]

    # Parallel fetch
    sem = asyncio.Semaphore(10)
    async def fetch_all():
        return await asyncio.gather(*[fetch_msg(slack_token, ch, ts, sem) for ch, ts in refs if ch and ts])

    results = asyncio.run(fetch_all())
    messages = [r for r in results if r]

    elapsed = (time.perf_counter() - start) * 1000

    # Extract message signatures for comparison
    msg_ids = sorted([f"{m['channel']}:{m['ts']}" for m in messages])

    return {
        "time_ms": elapsed,
        "messages_count": len(messages),
        "message_ids": msg_ids,
        "api_calls": 1 + len(refs),
        "llm_calls": 0,
        "tokens": 0,
    }


def run_mcp(slack_token: str, claude_key: str, query: str, limit: int) -> dict:
    """Run MCP approach - REAL Claude API calls."""
    start = time.perf_counter()

    tools = [
        {
            "name": "slack_search",
            "description": "Search Slack messages.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "slack_get_message",
            "description": "Get message by channel_id and ts.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string"},
                    "ts": {"type": "string"}
                },
                "required": ["channel_id", "ts"]
            }
        }
    ]

    messages = [{
        "role": "user",
        "content": f"Search Slack for '{query}' (limit {limit}), then fetch full content of each message. Return all message texts."
    }]

    collected = []
    total_input = 0
    total_output = 0
    llm_calls = 0
    api_calls = 0

    for _ in range(15):  # Max iterations
        try:
            response = claude_api_call(messages, tools, claude_key)
        except Exception as e:
            return {"error": str(e), "time_ms": (time.perf_counter() - start) * 1000}

        llm_calls += 1
        total_input += response.get("usage", {}).get("input_tokens", 0)
        total_output += response.get("usage", {}).get("output_tokens", 0)

        content = response.get("content", [])
        messages.append({"role": "assistant", "content": content})

        if response.get("stop_reason") == "end_turn":
            break

        if response.get("stop_reason") == "tool_use":
            tool_results = []
            for block in content:
                if block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    tool_input = block.get("input", {})
                    tool_id = block.get("id")

                    if tool_name == "slack_search":
                        r = slack_api_call("search.messages", slack_token, {
                            "query": tool_input.get("query", query),
                            "count": tool_input.get("limit", limit)
                        })
                        api_calls += 1
                        matches = r.get("messages", {}).get("matches", [])
                        result = {"messages": [
                            {"channel_id": m.get("channel", {}).get("id"), "ts": m.get("ts")}
                            for m in matches[:limit]
                        ]}
                    elif tool_name == "slack_get_message":
                        try:
                            r = slack_api_call("conversations.history", slack_token, {
                                "channel": tool_input.get("channel_id"),
                                "latest": tool_input.get("ts"),
                                "inclusive": "true", "limit": 1
                            })
                            api_calls += 1
                            if r.get("ok") and r.get("messages"):
                                m = r["messages"][0]
                                result = {
                                    "channel_id": tool_input.get("channel_id"),
                                    "ts": tool_input.get("ts"),
                                    "text": m.get("text", "")[:200]
                                }
                                collected.append({
                                    "channel": tool_input.get("channel_id"),
                                    "ts": tool_input.get("ts"),
                                    "text": m.get("text", "")[:100]
                                })
                            else:
                                result = {"error": "not found"}
                        except Exception as e:
                            result = {"error": str(e)}
                            api_calls += 1
                    else:
                        result = {"error": "unknown tool"}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(result)
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    elapsed = (time.perf_counter() - start) * 1000
    msg_ids = sorted([f"{m['channel']}:{m['ts']}" for m in collected])

    return {
        "time_ms": elapsed,
        "messages_count": len(collected),
        "message_ids": msg_ids,
        "api_calls": api_calls,
        "llm_calls": llm_calls,
        "tokens": total_input + total_output,
    }


def main():
    slack_token = os.environ.get("SLACK_USER_TOKEN")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")

    if not slack_token or not claude_key:
        print("Error: SLACK_USER_TOKEN and ANTHROPIC_API_KEY required")
        sys.exit(1)

    query = sys.argv[1] if len(sys.argv) > 1 else "budget"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    print(f"CONSISTENCY TEST: query='{query}', limit={limit}, runs={runs}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)

    composed_results = []
    mcp_results = []

    for i in range(runs):
        print(f"\n--- Run {i+1}/{runs} ---")

        # Composed
        print(f"  Composed: ", end="", flush=True)
        c = run_composed(slack_token, query, limit)
        composed_results.append(c)
        print(f"{c['time_ms']:.0f}ms, {c['messages_count']} msgs")

        # MCP
        print(f"  MCP:      ", end="", flush=True)
        m = run_mcp(slack_token, claude_key, query, limit)
        mcp_results.append(m)
        if "error" in m:
            print(f"ERROR: {m['error']}")
        else:
            print(f"{m['time_ms']:.0f}ms, {m['messages_count']} msgs, {m['llm_calls']} LLM calls, {m['tokens']} tokens")

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS ANALYSIS")
    print("=" * 80)

    # Timing
    composed_times = [r["time_ms"] for r in composed_results]
    mcp_times = [r["time_ms"] for r in mcp_results if "error" not in r]

    print(f"\n{'TIMING':<20}")
    print(f"  Composed: min={min(composed_times):.0f}ms, max={max(composed_times):.0f}ms, avg={sum(composed_times)/len(composed_times):.0f}ms")
    if mcp_times:
        print(f"  MCP:      min={min(mcp_times):.0f}ms, max={max(mcp_times):.0f}ms, avg={sum(mcp_times)/len(mcp_times):.0f}ms")

    # Consistency - do we get the same messages?
    print(f"\n{'CONSISTENCY':<20}")
    composed_msg_sets = [set(r["message_ids"]) for r in composed_results]
    mcp_msg_sets = [set(r["message_ids"]) for r in mcp_results if "error" not in r]

    # Check if composed results are identical across runs
    composed_identical = all(s == composed_msg_sets[0] for s in composed_msg_sets)
    print(f"  Composed results identical across {runs} runs: {composed_identical}")

    # Check if MCP results are identical across runs
    if mcp_msg_sets:
        mcp_identical = all(s == mcp_msg_sets[0] for s in mcp_msg_sets)
        print(f"  MCP results identical across {len(mcp_msg_sets)} runs: {mcp_identical}")

        # Check if MCP matches Composed
        mcp_matches_composed = all(s == composed_msg_sets[0] for s in mcp_msg_sets)
        print(f"  MCP matches Composed results: {mcp_matches_composed}")

    # Show actual message IDs from first run
    print(f"\n{'MESSAGES RETRIEVED (Run 1)':<30}")
    print(f"  Composed ({composed_results[0]['messages_count']}): {composed_results[0]['message_ids'][:3]}...")
    if mcp_results and "error" not in mcp_results[0]:
        print(f"  MCP ({mcp_results[0]['messages_count']}):      {mcp_results[0]['message_ids'][:3]}...")

    # Token usage
    print(f"\n{'TOKEN USAGE':<20}")
    total_tokens = sum(r.get("tokens", 0) for r in mcp_results)
    print(f"  Composed: 0 tokens (all {runs} runs)")
    print(f"  MCP: {total_tokens:,} tokens (all {runs} runs)")
    print(f"  Cost @ $3/$15 per M: ${total_tokens * 0.000009:.4f}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    if mcp_times:
        speedup = (sum(mcp_times)/len(mcp_times)) / (sum(composed_times)/len(composed_times))
        print(f"  Average speedup: {speedup:.1f}x faster")
    print(f"  Composed consistency: {'100% identical' if composed_identical else 'VARIES'}")
    if mcp_msg_sets:
        print(f"  MCP consistency: {'100% identical' if mcp_identical else 'VARIES across runs'}")
        print(f"  MCP matches Composed: {'YES' if mcp_matches_composed else 'NO - different results!'}")


if __name__ == "__main__":
    main()
