#!/usr/bin/env python3
"""
Multi-Query Benchmark: Compare Composed vs MCP across 5 different queries.
All measurements are REAL API calls.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen


def slack_api(method, token, params):
    url = f'https://slack.com/api/{method}?' + '&'.join(
        f'{k}={quote(str(v)) if k == "query" else v}' for k, v in params.items() if v
    )
    r = Request(url)
    r.add_header('Authorization', f'Bearer {token}')
    with urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


def claude_api(messages, api_key, tools=None):
    url = 'https://api.anthropic.com/v1/messages'
    payload = {'model': 'claude-sonnet-4-20250514', 'max_tokens': 4096, 'messages': messages}
    if tools:
        payload['tools'] = tools
    request = Request(url, json.dumps(payload).encode(), method='POST')
    request.add_header('Content-Type', 'application/json')
    request.add_header('x-api-key', api_key)
    request.add_header('anthropic-version', '2023-06-01')
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode())


async def fetch_msg(token, ch, ts, sem):
    async with sem:
        loop = asyncio.get_event_loop()
        try:
            r = await loop.run_in_executor(
                None,
                lambda: slack_api('conversations.history', token,
                    {'channel': ch, 'latest': ts, 'inclusive': 'true', 'limit': 1})
            )
            if r.get('ok') and r.get('messages'):
                return {'channel': ch, 'ts': ts, 'text': r['messages'][0].get('text', '')}
        except:
            pass
        return None


def run_composed(slack_token, claude_key, query, limit):
    """Run composed pipeline with LLM summarization."""
    start = time.perf_counter()

    # Search
    search_result = slack_api('search.messages', slack_token, {'query': query, 'count': limit})
    matches = search_result.get('messages', {}).get('matches', [])
    refs = [(m.get('channel', {}).get('id'), m.get('ts')) for m in matches]

    # Parallel fetch
    sem = asyncio.Semaphore(10)
    async def fetch_all():
        return await asyncio.gather(*[fetch_msg(slack_token, ch, ts, sem) for ch, ts in refs if ch and ts])
    messages = [m for m in asyncio.run(fetch_all()) if m]

    fetch_time = time.perf_counter() - start

    # Summarize with LLM
    if messages:
        context = '\n\n'.join([f'Message: {m["text"][:300]}' for m in messages])
        summary_prompt = f'Summarize these Slack messages about "{query}" in 2-3 sentences:\n\n{context}'
        response = claude_api([{'role': 'user', 'content': summary_prompt}], claude_key)
        summary = response['content'][0]['text']
        summary_tokens = response['usage']['input_tokens'] + response['usage']['output_tokens']
    else:
        summary = "No messages found."
        summary_tokens = 0

    total_time = time.perf_counter() - start

    return {
        'query': query,
        'time_ms': total_time * 1000,
        'fetch_time_ms': fetch_time * 1000,
        'messages': len(messages),
        'message_ids': sorted([f"{m['channel']}:{m['ts']}" for m in messages]),
        'tokens': summary_tokens,
        'llm_calls': 1 if messages else 0,
        'summary': summary[:200],
    }


def run_mcp(slack_token, claude_key, query, limit):
    """Run MCP approach with tool calls."""
    start = time.perf_counter()

    tools = [
        {'name': 'slack_search', 'description': 'Search Slack messages.',
         'input_schema': {'type': 'object', 'properties': {'query': {'type': 'string'}, 'limit': {'type': 'integer'}}, 'required': ['query']}},
        {'name': 'slack_get_message', 'description': 'Get full message by channel_id and ts.',
         'input_schema': {'type': 'object', 'properties': {'channel_id': {'type': 'string'}, 'ts': {'type': 'string'}}, 'required': ['channel_id', 'ts']}}
    ]

    msgs = [{'role': 'user', 'content': f"Search Slack for '{query}' (limit {limit}), fetch each message's full content, then summarize what you found in 2-3 sentences."}]
    collected = []
    total_tokens = 0
    llm_calls = 0
    summary = ""

    for _ in range(15):
        response = claude_api(msgs, claude_key, tools)
        llm_calls += 1
        total_tokens += response['usage']['input_tokens'] + response['usage']['output_tokens']

        content = response.get('content', [])
        msgs.append({'role': 'assistant', 'content': content})

        if response.get('stop_reason') == 'end_turn':
            for block in content:
                if block.get('type') == 'text':
                    summary = block['text']
            break

        if response.get('stop_reason') == 'tool_use':
            tool_results = []
            for block in content:
                if block.get('type') == 'tool_use':
                    name, inp, tid = block.get('name'), block.get('input', {}), block.get('id')

                    if name == 'slack_search':
                        r = slack_api('search.messages', slack_token, {'query': inp.get('query', query), 'count': inp.get('limit', limit)})
                        matches = r.get('messages', {}).get('matches', [])
                        result = {'messages': [{'channel_id': m.get('channel', {}).get('id'), 'ts': m.get('ts')} for m in matches[:limit]]}
                    elif name == 'slack_get_message':
                        try:
                            r = slack_api('conversations.history', slack_token, {'channel': inp.get('channel_id'), 'latest': inp.get('ts'), 'inclusive': 'true', 'limit': 1})
                            if r.get('ok') and r.get('messages'):
                                text = r['messages'][0].get('text', '')
                                collected.append({'channel': inp['channel_id'], 'ts': inp['ts'], 'text': text})
                                result = {'text': text[:300]}
                            else:
                                result = {'error': 'not found'}
                        except Exception as e:
                            result = {'error': str(e)}
                    else:
                        result = {'error': 'unknown'}

                    tool_results.append({'type': 'tool_result', 'tool_use_id': tid, 'content': json.dumps(result)})
            msgs.append({'role': 'user', 'content': tool_results})
        else:
            break

    total_time = time.perf_counter() - start

    return {
        'query': query,
        'time_ms': total_time * 1000,
        'messages': len(collected),
        'message_ids': sorted([f"{m['channel']}:{m['ts']}" for m in collected]),
        'tokens': total_tokens,
        'llm_calls': llm_calls,
        'summary': summary[:200],
    }


def main():
    slack_token = os.environ.get('SLACK_USER_TOKEN')
    claude_key = os.environ.get('ANTHROPIC_API_KEY')

    if not slack_token or not claude_key:
        print("Error: SLACK_USER_TOKEN and ANTHROPIC_API_KEY required")
        sys.exit(1)

    # 5 diverse queries
    queries = [
        ("budget", "Financial/planning topic"),
        ("deployment", "Technical/engineering topic"),
        ("meeting notes", "General collaboration"),
        ("deadline", "Time-sensitive/urgent"),
        ("from:@lee", "Person-specific search"),
    ]

    limit = 5

    print("=" * 90)
    print("MULTI-QUERY BENCHMARK: Composed Pipeline vs MCP Tool Calls")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Messages per query: {limit}")
    print("=" * 90)

    results = []

    for query, description in queries:
        print(f"\n{'─' * 90}")
        print(f"QUERY: \"{query}\" ({description})")
        print("─" * 90)

        # Run Composed
        print("  [Composed] Running...", end=" ", flush=True)
        composed = run_composed(slack_token, claude_key, query, limit)
        print(f"Done: {composed['time_ms']:.0f}ms, {composed['messages']} msgs, {composed['tokens']} tokens")

        # Run MCP
        print("  [MCP]      Running...", end=" ", flush=True)
        mcp = run_mcp(slack_token, claude_key, query, limit)
        print(f"Done: {mcp['time_ms']:.0f}ms, {mcp['messages']} msgs, {mcp['tokens']} tokens")

        # Compare
        same_messages = set(composed['message_ids']) == set(mcp['message_ids'])
        speedup = mcp['time_ms'] / composed['time_ms'] if composed['time_ms'] > 0 else 0
        token_savings = mcp['tokens'] - composed['tokens']

        print(f"\n  Results match: {'✅ YES' if same_messages else '❌ NO'}")
        print(f"  Speedup: {speedup:.1f}x faster")
        print(f"  Token savings: {token_savings} ({token_savings/mcp['tokens']*100:.0f}% saved)" if mcp['tokens'] > 0 else "  Token savings: N/A")

        print(f"\n  Composed summary: {composed['summary'][:100]}...")
        print(f"  MCP summary:      {mcp['summary'][:100]}...")

        results.append({
            'query': query,
            'composed': composed,
            'mcp': mcp,
            'same_messages': same_messages,
            'speedup': speedup,
            'token_savings': token_savings,
        })

    # Summary
    print("\n" + "=" * 90)
    print("SUMMARY ACROSS ALL QUERIES")
    print("=" * 90)

    total_composed_time = sum(r['composed']['time_ms'] for r in results)
    total_mcp_time = sum(r['mcp']['time_ms'] for r in results)
    total_composed_tokens = sum(r['composed']['tokens'] for r in results)
    total_mcp_tokens = sum(r['mcp']['tokens'] for r in results)
    all_match = all(r['same_messages'] for r in results)

    print(f"\n{'Metric':<25} {'Composed':<20} {'MCP':<20} {'Difference':<20}")
    print("-" * 85)
    print(f"{'Total Time (ms)':<25} {total_composed_time:<20.0f} {total_mcp_time:<20.0f} {total_mcp_time/total_composed_time:.1f}x slower")
    print(f"{'Total Tokens':<25} {total_composed_tokens:<20} {total_mcp_tokens:<20} {total_mcp_tokens - total_composed_tokens} saved")
    print(f"{'Results Match':<25} {'—':<20} {'—':<20} {'✅ All match' if all_match else '❌ Some differ'}")

    avg_speedup = sum(r['speedup'] for r in results) / len(results)
    avg_token_savings_pct = (total_mcp_tokens - total_composed_tokens) / total_mcp_tokens * 100 if total_mcp_tokens > 0 else 0

    print(f"\n{'Average Speedup':<25} {avg_speedup:.1f}x faster")
    print(f"{'Token Savings':<25} {avg_token_savings_pct:.0f}%")

    # Cost estimate
    cost_composed = total_composed_tokens * 0.000009  # ~$9/M tokens avg
    cost_mcp = total_mcp_tokens * 0.000009
    print(f"\n{'Cost (5 queries)':<25} ${cost_composed:.4f}{'':<13} ${cost_mcp:.4f}{'':<13} ${cost_mcp - cost_composed:.4f} saved")

    print("\n" + "=" * 90)
    print("PER-QUERY BREAKDOWN")
    print("=" * 90)
    print(f"\n{'Query':<20} {'Composed (ms)':<15} {'MCP (ms)':<15} {'Speedup':<10} {'Tokens Saved':<15} {'Match':<8}")
    print("-" * 83)
    for r in results:
        print(f"{r['query']:<20} {r['composed']['time_ms']:<15.0f} {r['mcp']['time_ms']:<15.0f} {r['speedup']:<10.1f}x {r['token_savings']:<15} {'✅' if r['same_messages'] else '❌'}")


if __name__ == "__main__":
    main()
