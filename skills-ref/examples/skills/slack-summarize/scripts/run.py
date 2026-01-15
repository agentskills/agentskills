#!/usr/bin/env python3
"""
Slack Summarize Skill - Fan-in aggregation and summarization.

Takes multiple messages, produces structured summary + LLM prompt.
All analysis is deterministic Python - LLM only needed for final prose.
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime


def parse_datetime(dt_str: str) -> datetime | None:
    """Parse ISO datetime string."""
    if not dt_str:
        return None
    try:
        # Handle both with and without timezone
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


def analyze_messages(messages: list[dict], question: str | None = None) -> dict:
    """
    Analyze messages and produce structured summary.

    This is all deterministic Python - no LLM calls.
    """
    if not messages:
        return {"error": "No messages to analyze"}

    # Collect metadata
    channels = defaultdict(lambda: {"count": 0, "participants": set(), "messages": []})
    participants = set()
    dates = []
    daily_counts = defaultdict(lambda: {"count": 0, "channels": set()})

    for msg in messages:
        channel = msg.get("channel_name", "unknown")
        username = msg.get("username", "unknown")
        dt = parse_datetime(msg.get("datetime", ""))

        # Track by channel
        channels[channel]["count"] += 1
        channels[channel]["participants"].add(username)
        channels[channel]["messages"].append({
            "user": username,
            "text": msg.get("text", "")[:500],  # Truncate for summary
            "datetime": msg.get("datetime", ""),
            "reactions": msg.get("reactions", []),
        })

        # Track participants
        participants.add(username)

        # Track dates
        if dt:
            dates.append(dt)
            date_key = dt.strftime("%Y-%m-%d")
            daily_counts[date_key]["count"] += 1
            daily_counts[date_key]["channels"].add(channel)

    # Build date range
    date_range = {}
    if dates:
        dates.sort()
        date_range = {
            "earliest": dates[0].isoformat(),
            "latest": dates[-1].isoformat(),
        }

    # Build timeline
    timeline = [
        {"date": date, "count": data["count"], "channels": sorted(data["channels"])}
        for date, data in sorted(daily_counts.items())
    ]

    # Build channel summaries (convert sets to lists for JSON)
    by_channel = {}
    for channel, data in channels.items():
        # Sort messages by reactions (most reacted first) as proxy for importance
        sorted_msgs = sorted(
            data["messages"],
            key=lambda m: sum(r.get("count", 0) for r in m.get("reactions", [])),
            reverse=True
        )
        by_channel[channel] = {
            "count": data["count"],
            "participants": sorted(data["participants"]),
            "key_messages": sorted_msgs[:3],  # Top 3 by reactions
        }

    # Build structured result
    result = {
        "meta": {
            "total_messages": len(messages),
            "channels": sorted(channels.keys()),
            "participants": sorted(participants),
            "date_range": date_range,
        },
        "by_channel": by_channel,
        "timeline": timeline,
    }

    return result


def generate_llm_prompt(analysis: dict, messages: list[dict], question: str | None = None) -> str:
    """
    Generate a prompt for LLM summarization.

    The prompt includes all context needed - LLM just needs to synthesize.
    """
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

    # Sort messages chronologically for the prompt
    sorted_messages = sorted(messages, key=lambda m: m.get("datetime", ""))

    for msg in sorted_messages:
        dt = msg.get("datetime", "")[:16]  # Trim to minute
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


def main():
    parser = argparse.ArgumentParser(
        description="Summarize Slack messages with structured analysis"
    )
    parser.add_argument("--input", "-i", help="JSON file with message content (or use stdin)")
    parser.add_argument("--question", "-q", help="Question to answer about the messages")
    parser.add_argument("--format", "-f", choices=["structured", "prompt", "both"],
                        default="both", help="Output format (default: both)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

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

    messages = data.get("messages", [])
    if not messages:
        print("Error: No messages found in input", file=sys.stderr)
        sys.exit(1)

    # Analyze
    analysis = analyze_messages(messages, args.question)

    # Generate LLM prompt
    llm_prompt = generate_llm_prompt(analysis, messages, args.question)

    # Build output based on format
    if args.format == "structured":
        output = analysis
    elif args.format == "prompt":
        output = {"llm_prompt": llm_prompt}
    else:  # both
        output = {**analysis, "llm_prompt": llm_prompt}

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        meta = analysis.get("meta", {})
        print("=" * 70)
        print("SLACK MESSAGE SUMMARY")
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
            print("LLM PROMPT:")
            print("=" * 70)
            print(llm_prompt)

    return 0


if __name__ == "__main__":
    sys.exit(main())
