#!/usr/bin/env python3
"""
Slack Read Skill - Fetch full message content in parallel.

Fan-out pattern: takes message references, fetches all in parallel.
Uses asyncio for concurrent API calls.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


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


async def fetch_message(
    token: str, channel_id: str, ts: str, ref: dict, semaphore: asyncio.Semaphore
) -> dict | None:
    """Fetch a single message with rate limiting via semaphore."""
    async with semaphore:
        # Run blocking API call in thread pool
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
            # Log error but continue with other messages
            print(f"Warning: Failed to fetch {channel_id}/{ts}: {e}", file=sys.stderr)
            return None


async def fetch_all_messages(
    token: str, refs: list[dict], max_parallel: int = 10
) -> list[dict]:
    """Fetch all messages in parallel with rate limiting."""
    semaphore = asyncio.Semaphore(max_parallel)

    tasks = [
        fetch_message(token, ref["channel_id"], ref["ts"], ref, semaphore)
        for ref in refs
        if ref.get("channel_id") and ref.get("ts")
    ]

    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch full Slack message content from references"
    )
    parser.add_argument("--input", "-i", help="JSON file with message refs (or use stdin)")
    parser.add_argument("--max-parallel", "-p", type=int, default=10,
                        help="Max concurrent requests (default: 10)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Get token (prefer user token, fall back to bot token)
    token = os.environ.get("SLACK_USER_TOKEN") or os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("Error: SLACK_USER_TOKEN or SLACK_BOT_TOKEN required", file=sys.stderr)
        sys.exit(1)

    # Read input
    try:
        if args.input:
            with open(args.input) as f:
                data = json.load(f)
        elif not sys.stdin.isatty():
            data = json.load(sys.stdin)
        else:
            print("Error: Provide --input file or pipe JSON to stdin", file=sys.stderr)
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract message refs
    refs = data.get("messages", [])
    if not refs:
        print("Error: No messages found in input", file=sys.stderr)
        sys.exit(1)

    # Fetch in parallel
    try:
        messages = asyncio.run(fetch_all_messages(token, refs, args.max_parallel))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Sort by timestamp (newest first)
    messages.sort(key=lambda m: m.get("ts", ""), reverse=True)

    result = {
        "fetched": len(messages),
        "messages": messages,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Fetched: {result['fetched']} messages")
        print("=" * 70)
        for msg in messages:
            dt = msg["datetime"][:19] if msg["datetime"] else msg["ts"]
            print(f"#{msg['channel_name']} | @{msg['username']} | {dt}")
            print(f"{msg['text'][:500]}")
            if msg["reactions"]:
                reactions = " ".join(f":{r['name']}:{r['count']}" for r in msg["reactions"])
                print(f"Reactions: {reactions}")
            print("-" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
