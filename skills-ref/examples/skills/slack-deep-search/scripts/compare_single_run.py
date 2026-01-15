#!/usr/bin/env python3
"""
Compare a single run: Do Composed and MCP get the SAME messages?
"""

import asyncio
import json
import os
import sys
import time
from urllib.parse import quote
from urllib.request import Request, urlopen


def slack_api_call(method, token, params):
    url = f"https://slack.com/api/{method}"
    query_parts = [f"{k}={quote(str(v)) if k == 'query' else v}" for k, v in params.items() if v]
    if query_parts:
        url = f"{url}?{'&'.join(query_parts)}"
    request = Request(url)
    request.add_header("Authorization", f"Bearer {token}")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def claude_api_call(messages, tools, api_key):
    url = "https://api.anthropic.com/v1/messages"
    payload = {"model": "claude-sonnet-4-20250514", "max_tokens": 4096, "tools": tools, "messages": messages}
    request = Request(url, json.dumps(payload).encode(), method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("x-api-key", api_key)
    request.add_header("anthropic-version", "2023-06-01")
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode())


async def fetch_msg(token, ch, ts, sem):
    async with sem:
        loop = asyncio.get_event_loop()
        try:
            r = await loop.run_in_executor(None, lambda: slack_api_call(
                "conversations.history", token, {"channel": ch, "latest": ts, "inclusive": "true", "limit": 1}
            ))
            if r.get("ok") and r.get("messages"):
                return {"channel": ch, "ts": ts, "text": r["messages"][0].get("text", "")[:80]}
        except:
            pass
        return None


def run_composed(slack_token, query, limit):
    start = time.perf_counter()
    search_result = slack_api_call("search.messages", slack_token, {"query": query, "count": limit})
    matches = search_result.get("messages", {}).get("matches", [])
    refs = [(m.get("channel", {}).get("id"), m.get("ts")) for m in matches]

    sem = asyncio.Semaphore(10)
    async def fetch_all():
        return await asyncio.gather(*[fetch_msg(slack_token, ch, ts, sem) for ch, ts in refs if ch and ts])
    results = asyncio.run(fetch_all())
    messages = sorted([r for r in results if r], key=lambda x: x["ts"])

    return {
        "time_ms": (time.perf_counter() - start) * 1000,
        "messages": messages,
    }


def run_mcp(slack_token, claude_key, query, limit):
    start = time.perf_counter()
    tools = [
        {"name": "slack_search", "description": "Search Slack.", "input_schema": {
            "type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["query"]
        }},
        {"name": "slack_get_message", "description": "Get message.", "input_schema": {
            "type": "object", "properties": {"channel_id": {"type": "string"}, "ts": {"type": "string"}}, "required": ["channel_id", "ts"]
        }}
    ]

    msgs = [{"role": "user", "content": f"Search Slack for '{query}' (limit {limit}), fetch each message, return texts."}]
    collected = []
    total_tokens = 0
    llm_calls = 0

    for _ in range(15):
        response = claude_api_call(msgs, tools, claude_key)
        llm_calls += 1
        total_tokens += response.get("usage", {}).get("input_tokens", 0) + response.get("usage", {}).get("output_tokens", 0)
        content = response.get("content", [])
        msgs.append({"role": "assistant", "content": content})

        if response.get("stop_reason") == "end_turn":
            break

        if response.get("stop_reason") == "tool_use":
            tool_results = []
            for block in content:
                if block.get("type") == "tool_use":
                    name, inp, tid = block.get("name"), block.get("input", {}), block.get("id")
                    if name == "slack_search":
                        r = slack_api_call("search.messages", slack_token, {"query": inp.get("query", query), "count": inp.get("limit", limit)})
                        result = {"messages": [{"channel_id": m.get("channel", {}).get("id"), "ts": m.get("ts")} for m in r.get("messages", {}).get("matches", [])[:limit]]}
                    elif name == "slack_get_message":
                        try:
                            r = slack_api_call("conversations.history", slack_token, {"channel": inp.get("channel_id"), "latest": inp.get("ts"), "inclusive": "true", "limit": 1})
                            if r.get("ok") and r.get("messages"):
                                result = {"channel_id": inp["channel_id"], "ts": inp["ts"], "text": r["messages"][0].get("text", "")[:80]}
                                collected.append({"channel": inp["channel_id"], "ts": inp["ts"], "text": r["messages"][0].get("text", "")[:80]})
                            else:
                                result = {"error": "not found"}
                        except Exception as e:
                            result = {"error": str(e)}
                    else:
                        result = {"error": "unknown"}
                    tool_results.append({"type": "tool_result", "tool_use_id": tid, "content": json.dumps(result)})
            msgs.append({"role": "user", "content": tool_results})
        else:
            break

    return {
        "time_ms": (time.perf_counter() - start) * 1000,
        "messages": sorted(collected, key=lambda x: x["ts"]),
        "tokens": total_tokens,
        "llm_calls": llm_calls,
    }


def main():
    slack_token = os.environ.get("SLACK_USER_TOKEN")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    query = sys.argv[1] if len(sys.argv) > 1 else "budget"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print(f"SINGLE RUN COMPARISON: query='{query}', limit={limit}")
    print("=" * 80)

    print("\n[1] Running Composed Pipeline...")
    composed = run_composed(slack_token, query, limit)
    print(f"    Time: {composed['time_ms']:.0f}ms, Messages: {len(composed['messages'])}")

    print("\n[2] Running MCP (Claude API)...")
    mcp = run_mcp(slack_token, claude_key, query, limit)
    print(f"    Time: {mcp['time_ms']:.0f}ms, Messages: {len(mcp['messages'])}, LLM calls: {mcp['llm_calls']}, Tokens: {mcp['tokens']}")

    print("\n" + "=" * 80)
    print("MESSAGE COMPARISON")
    print("=" * 80)

    composed_ids = set(f"{m['channel']}:{m['ts']}" for m in composed["messages"])
    mcp_ids = set(f"{m['channel']}:{m['ts']}" for m in mcp["messages"])

    print(f"\nComposed retrieved: {len(composed_ids)} messages")
    print(f"MCP retrieved:      {len(mcp_ids)} messages")
    print(f"Overlap:            {len(composed_ids & mcp_ids)} messages")
    print(f"Only in Composed:   {len(composed_ids - mcp_ids)}")
    print(f"Only in MCP:        {len(mcp_ids - composed_ids)}")

    print(f"\nSAME RESULTS: {composed_ids == mcp_ids}")

    print("\n" + "-" * 80)
    print("COMPOSED MESSAGES:")
    for m in composed["messages"]:
        print(f"  [{m['channel']}:{m['ts'][:10]}] {m['text'][:60]}...")

    print("\nMCP MESSAGES:")
    for m in mcp["messages"]:
        print(f"  [{m['channel']}:{m['ts'][:10]}] {m['text'][:60]}...")

    print("\n" + "=" * 80)
    print("METRICS")
    print("=" * 80)
    print(f"  Composed: {composed['time_ms']:.0f}ms, 0 tokens")
    print(f"  MCP:      {mcp['time_ms']:.0f}ms, {mcp['tokens']} tokens")
    print(f"  Speedup:  {mcp['time_ms']/composed['time_ms']:.1f}x faster")


if __name__ == "__main__":
    main()
