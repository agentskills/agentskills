#!/usr/bin/env python3
"""
Regression Checker

Checks comparison results and exits with error if regressions
exceed threshold. Used in CI to fail builds on performance regression.

Usage:
    python scripts/check-regressions.py \
        --comparison reports/comparison.json \
        --threshold 10
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Check for regressions")
    parser.add_argument("--comparison", type=str, required=True, help="Comparison JSON")
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Max allowed regression % before failing",
    )
    parser.add_argument(
        "--max-regressions",
        type=int,
        default=3,
        help="Max number of regressions allowed",
    )

    args = parser.parse_args()

    # Load comparison
    try:
        with open(args.comparison) as f:
            comparison = json.load(f)
    except FileNotFoundError:
        print(f"Warning: No comparison file found, skipping regression check")
        sys.exit(0)

    regressions = comparison.get("regressions", [])

    if not regressions:
        print("✅ No performance regressions detected")
        sys.exit(0)

    # Check severity
    critical_regressions = [
        r for r in regressions if r.get("percent_change", 0) > args.threshold
    ]

    print(f"Found {len(regressions)} regression(s):")
    for reg in regressions:
        severity = "CRITICAL" if reg.get("percent_change", 0) > args.threshold else "WARNING"
        print(
            f"  [{severity}] {reg['skill']}: "
            f"+{reg['percent_change']:.1f}% "
            f"({reg['baseline_mean_ms']:.2f}ms → {reg['candidate_mean_ms']:.2f}ms)"
        )

    if critical_regressions:
        print(f"\n❌ {len(critical_regressions)} critical regression(s) exceed {args.threshold}% threshold")
        sys.exit(1)

    if len(regressions) > args.max_regressions:
        print(f"\n❌ Too many regressions ({len(regressions)} > {args.max_regressions})")
        sys.exit(1)

    print(f"\n⚠️ {len(regressions)} minor regression(s) within acceptable limits")
    sys.exit(0)


if __name__ == "__main__":
    main()
