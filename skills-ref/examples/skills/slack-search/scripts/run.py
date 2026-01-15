#!/usr/bin/env python3
"""
Slack Search Skill - Search messages and return references.

This is real working code that calls the Slack API.
Requires SLACK_USER_TOKEN (user tokens can search, bot tokens cannot).
"""

import argparse
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def slack_api_call(method: str, token: str, params: dict[str, Any]) -> dict:
    """Make a Slack API call using urllib (no dependencies)."""
    url = f"https://slack.com/api/{method}"

    # Build query string
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


def search_messages(token: str, query: str, limit: int = 20) -> dict:
    """
    Search Slack messages.

    Returns structured message references for downstream processing.
    """
    # URL encode the query
    from urllib.parse import quote
    encoded_query = quote(query)

    response = slack_api_call(
        "search.messages",
        token,
        {"query": encoded_query, "count": min(limit, 100), "sort": "timestamp"}
    )

    messages = response.get("messages", {})
    matches = messages.get("matches", [])
    total = messages.get("total", 0)

    # Extract message references with metadata
    refs = []
    for msg in matches:
        refs.append({
            "channel_id": msg.get("channel", {}).get("id", ""),
            "channel_name": msg.get("channel", {}).get("name", ""),
            "ts": msg.get("ts", ""),
            "permalink": msg.get("permalink", ""),
            "user_id": msg.get("user", ""),
            "username": msg.get("username", ""),
            "snippet": msg.get("text", "")[:200],  # First 200 chars as preview
        })

    return {
        "query": query,
        "total": total,
        "returned": len(refs),
        "messages": refs,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Search Slack messages and return references"
    )
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Get token
    token = os.environ.get("SLACK_USER_TOKEN")
    if not token:
        print("Error: SLACK_USER_TOKEN environment variable required", file=sys.stderr)
        print("Note: Bot tokens (xoxb-*) cannot search. Use a user token (xoxp-*).", file=sys.stderr)
        sys.exit(1)

    try:
        result = search_messages(token, args.query, args.limit)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Search: {result['query']}")
            print(f"Found: {result['total']} total, showing {result['returned']}")
            print("-" * 60)
            for msg in result["messages"]:
                print(f"#{msg['channel_name']} | @{msg['username']} | {msg['ts']}")
                print(f"  {msg['snippet'][:80]}...")
                print(f"  {msg['permalink']}")
                print()

        return 0

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
