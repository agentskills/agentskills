#!/usr/bin/env python3
"""
Slack Deep Search - Composed skill pipeline.

Chains: slack-search → slack-read → slack-summarize

All orchestration is deterministic Python. The LLM is only needed
at the very end to interpret the structured summary.
"""

import argparse
import asyncio
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


# =============================================================================
# Shared utilities
# =============================================================================

def slack_api_call(method: str, token: str, params: dict[str, Any]) -> dict:
    """Make a Slack API call using urllib (no dependencies)."""
    url = f"https://slack.com/api/{method}"

    query_parts = [f"{k}={v}" for k, v in params.items() if v is not None]
    if query_parts:
        url = f"{url}?{'&'.join(query_parts)}"

    request = Request(url)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode())
            if not data.get("ok"):
                error = data.get("error", "unknown_error")
                raise RuntimeError(f"Slack API error: {error}")
            return data
    except HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code}: {e.reason}")
    except URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")


def ts_to_datetime(ts: str) -> str:
    """Convert Slack timestamp to ISO datetime."""
    try:
        unix_ts = float(ts.split(".")[0])
        dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
        return dt.isoformat()
    except (ValueError, IndexError):
        return ""


# =============================================================================
# Stage 1: Search
# =============================================================================

def search_messages(token: str, query: str, limit: int = 20) -> dict:
    """Search Slack and return message references."""
    encoded_query = quote(query)

    response = slack_api_call(
        "search.messages",
        token,
        {"query": encoded_query, "count": min(limit, 100), "sort": "timestamp"}
    )

    messages = response.get("messages", {})
    matches = messages.get("matches", [])
    total = messages.get("total", 0)

    refs = []
    for msg in matches:
        refs.append({
            "channel_id": msg.get("channel", {}).get("id", ""),
            "channel_name": msg.get("channel", {}).get("name", ""),
            "ts": msg.get("ts", ""),
            "permalink": msg.get("permalink", ""),
            "user_id": msg.get("user", ""),
            "username": msg.get("username", ""),
            "snippet": msg.get("text", "")[:200],
        })

    return {"query": query, "total": total, "returned": len(refs), "messages": refs}


# =============================================================================
# Stage 2: Read (fan-out)
# =============================================================================

async def fetch_message(
    token: str, channel_id: str, ts: str, ref: dict, semaphore: asyncio.Semaphore
) -> dict | None:
    """Fetch a single message with rate limiting."""
    async with semaphore:
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: slack_api_call(
                    "conversations.history",
                    token,
                    {"channel": channel_id, "latest": ts, "inclusive": "true", "limit": 1}
                )
            )

            messages = response.get("messages", [])
            if not messages:
                return None

            msg = messages[0]
            return {
                "channel_id": channel_id,
                "channel_name": ref.get("channel_name", ""),
                "ts": ts,
                "datetime": ts_to_datetime(ts),
                "user_id": msg.get("user", ""),
                "username": ref.get("username", ""),
                "text": msg.get("text", ""),
                "permalink": ref.get("permalink", ""),
                "thread_ts": msg.get("thread_ts"),
                "reply_count": msg.get("reply_count", 0),
                "reactions": [
                    {"name": r.get("name"), "count": r.get("count", 0)}
                    for r in msg.get("reactions", [])
                ],
            }
        except RuntimeError as e:
            print(f"Warning: Failed to fetch {channel_id}/{ts}: {e}", file=sys.stderr)
            return None


async def read_messages(token: str, refs: list[dict], max_parallel: int = 10) -> list[dict]:
    """Fetch all messages in parallel."""
    semaphore = asyncio.Semaphore(max_parallel)

    tasks = [
        fetch_message(token, ref["channel_id"], ref["ts"], ref, semaphore)
        for ref in refs
        if ref.get("channel_id") and ref.get("ts")
    ]

    results = await asyncio.gather(*tasks)
    messages = [r for r in results if r is not None]
    messages.sort(key=lambda m: m.get("ts", ""), reverse=True)
    return messages


# =============================================================================
# Stage 3: Summarize (fan-in)
# =============================================================================

def parse_datetime(dt_str: str) -> datetime | None:
    """Parse ISO datetime string."""
    if not dt_str:
        return None
    try:
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


def summarize_messages(messages: list[dict], question: str | None = None) -> dict:
    """Analyze and summarize messages."""
    if not messages:
        return {"error": "No messages to analyze"}

    channels = defaultdict(lambda: {"count": 0, "participants": set(), "messages": []})
    participants = set()
    dates = []
    daily_counts = defaultdict(lambda: {"count": 0, "channels": set()})

    for msg in messages:
        channel = msg.get("channel_name", "unknown")
        username = msg.get("username", "unknown")
        dt = parse_datetime(msg.get("datetime", ""))

        channels[channel]["count"] += 1
        channels[channel]["participants"].add(username)
        channels[channel]["messages"].append({
            "user": username,
            "text": msg.get("text", "")[:500],
            "datetime": msg.get("datetime", ""),
            "reactions": msg.get("reactions", []),
        })

        participants.add(username)

        if dt:
            dates.append(dt)
            date_key = dt.strftime("%Y-%m-%d")
            daily_counts[date_key]["count"] += 1
            daily_counts[date_key]["channels"].add(channel)

    date_range = {}
    if dates:
        dates.sort()
        date_range = {
            "earliest": dates[0].isoformat(),
            "latest": dates[-1].isoformat(),
        }

    timeline = [
        {"date": date, "count": data["count"], "channels": sorted(data["channels"])}
        for date, data in sorted(daily_counts.items())
    ]

    by_channel = {}
    for channel, data in channels.items():
        sorted_msgs = sorted(
            data["messages"],
            key=lambda m: sum(r.get("count", 0) for r in m.get("reactions", [])),
            reverse=True
        )
        by_channel[channel] = {
            "count": data["count"],
            "participants": sorted(data["participants"]),
            "key_messages": sorted_msgs[:3],
        }

    return {
        "meta": {
            "total_messages": len(messages),
            "channels": sorted(channels.keys()),
            "participants": sorted(participants),
            "date_range": date_range,
        },
        "by_channel": by_channel,
        "timeline": timeline,
    }


def generate_llm_prompt(analysis: dict, messages: list[dict], question: str | None = None) -> str:
    """Generate prompt for LLM summarization."""
    meta = analysis.get("meta", {})

    prompt_parts = [
        "# Slack Message Analysis",
        "",
        "## Context",
        f"- Total messages: {meta.get('total_messages', 0)}",
        f"- Channels: {', '.join(meta.get('channels', []))}",
        f"- Participants: {', '.join(meta.get('participants', []))}",
    ]

    date_range = meta.get("date_range", {})
    if date_range:
        prompt_parts.append(f"- Date range: {date_range.get('earliest', '')} to {date_range.get('latest', '')}")

    prompt_parts.extend(["", "## Messages (chronological)", ""])

    sorted_messages = sorted(messages, key=lambda m: m.get("datetime", ""))

    for msg in sorted_messages:
        dt = msg.get("datetime", "")[:16]
        channel = msg.get("channel_name", "")
        user = msg.get("username", "")
        text = msg.get("text", "").strip()

        prompt_parts.append(f"**[{dt}] #{channel} @{user}:**")
        prompt_parts.append(text)
        prompt_parts.append("")

    if question:
        prompt_parts.extend([
            "## Question to Answer",
            question,
            "",
            "## Instructions",
            "Based on the messages above, answer the question. Cite specific messages when relevant.",
        ])
    else:
        prompt_parts.extend([
            "## Instructions",
            "Summarize the key points from these messages. Group by topic if there are multiple threads.",
            "Note any decisions made, action items, or unresolved questions.",
        ])

    return "\n".join(prompt_parts)


# =============================================================================
# Main pipeline
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Deep Slack search with parallel fetch and summarization"
    )
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--question", help="Question to answer about results")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max messages (default: 20)")
    parser.add_argument("--format", "-f", choices=["structured", "prompt", "both"],
                        default="both", help="Output format")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show pipeline progress")
    args = parser.parse_args()

    # Get token
    token = os.environ.get("SLACK_USER_TOKEN")
    if not token:
        print("Error: SLACK_USER_TOKEN required (bot tokens cannot search)", file=sys.stderr)
        sys.exit(1)

    try:
        # Stage 1: Search
        if args.verbose:
            print(f"[1/3] Searching: {args.query}", file=sys.stderr)

        search_result = search_messages(token, args.query, args.limit)
        refs = search_result["messages"]

        if not refs:
            print(f"No messages found for query: {args.query}", file=sys.stderr)
            sys.exit(0)

        if args.verbose:
            print(f"      Found {search_result['total']} total, fetching {len(refs)}", file=sys.stderr)

        # Stage 2: Read (fan-out)
        if args.verbose:
            print(f"[2/3] Fetching {len(refs)} messages in parallel...", file=sys.stderr)

        messages = asyncio.run(read_messages(token, refs))

        if args.verbose:
            print(f"      Retrieved {len(messages)} messages", file=sys.stderr)

        # Stage 3: Summarize (fan-in)
        if args.verbose:
            print("[3/3] Analyzing and summarizing...", file=sys.stderr)

        analysis = summarize_messages(messages, args.question)
        llm_prompt = generate_llm_prompt(analysis, messages, args.question)

        # Build output
        if args.format == "structured":
            output = {"query": args.query, **analysis}
        elif args.format == "prompt":
            output = {"query": args.query, "llm_prompt": llm_prompt}
        else:
            output = {"query": args.query, **analysis, "llm_prompt": llm_prompt}

        # Output
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            meta = analysis.get("meta", {})
            print("=" * 70)
            print(f"DEEP SEARCH: {args.query}")
            print("=" * 70)
            print(f"Messages: {meta.get('total_messages', 0)}")
            print(f"Channels: {', '.join(meta.get('channels', []))}")
            print(f"Participants: {', '.join(meta.get('participants', []))}")

            date_range = meta.get("date_range", {})
            if date_range:
                print(f"Period: {date_range.get('earliest', '')[:10]} to {date_range.get('latest', '')[:10]}")

            print("\n" + "-" * 70)
            print("BY CHANNEL:")
            for channel, data in analysis.get("by_channel", {}).items():
                print(f"\n#{channel} ({data['count']} messages)")
                print(f"  Participants: {', '.join(data['participants'])}")
                if data.get("key_messages"):
                    print("  Key messages:")
                    for msg in data["key_messages"][:2]:
                        print(f"    - @{msg['user']}: {msg['text'][:80]}...")

            if args.format in ["prompt", "both"]:
                print("\n" + "=" * 70)
                print("LLM PROMPT (copy to Claude/GPT for summarization):")
                print("=" * 70)
                print(llm_prompt)

        return 0

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
