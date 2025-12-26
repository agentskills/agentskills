#!/usr/bin/env python3
"""
Benchmark Comparison Script

Compares candidate benchmarks against baseline and generates
a comparison report highlighting regressions and improvements.

Usage:
    python scripts/compare-benchmarks.py \
        --baseline benchmarks/baseline.json \
        --candidate benchmarks/isolated-candidate.json \
        --output reports/comparison.json
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Comparison:
    """Comparison between baseline and candidate for a skill."""

    skill: str
    baseline_mean_ms: float
    candidate_mean_ms: float
    percent_change: float
    status: str  # improved, regressed, unchanged, new


def compare_benchmarks(
    baseline: list[dict], candidate: list[dict], threshold: float = 5.0
) -> dict:
    """Compare candidate against baseline."""
    baseline_lookup = {b["skill"]: b for b in baseline}

    improvements = []
    regressions = []
    unchanged = []
    new_skills = []

    for cand in candidate:
        skill_name = cand.get("skill", "")
        base = baseline_lookup.get(skill_name)

        if not base:
            new_skills.append(
                Comparison(
                    skill=skill_name,
                    baseline_mean_ms=0,
                    candidate_mean_ms=cand.get("exec_time_mean_ms", 0),
                    percent_change=0,
                    status="new",
                )
            )
            continue

        baseline_mean = base.get("exec_time_mean_ms", 0)
        candidate_mean = cand.get("exec_time_mean_ms", 0)

        if baseline_mean == 0:
            percent_change = 0
        else:
            percent_change = ((candidate_mean - baseline_mean) / baseline_mean) * 100

        comparison = Comparison(
            skill=skill_name,
            baseline_mean_ms=baseline_mean,
            candidate_mean_ms=candidate_mean,
            percent_change=percent_change,
            status="unchanged",
        )

        if percent_change < -threshold:
            comparison.status = "improved"
            improvements.append(comparison)
        elif percent_change > threshold:
            comparison.status = "regressed"
            regressions.append(comparison)
        else:
            comparison.status = "unchanged"
            unchanged.append(comparison)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "threshold_percent": threshold,
        "summary": {
            "improvements": len(improvements),
            "regressions": len(regressions),
            "unchanged": len(unchanged),
            "new_skills": len(new_skills),
        },
        "improvements": [asdict(c) for c in sorted(improvements, key=lambda x: x.percent_change)],
        "regressions": [asdict(c) for c in sorted(regressions, key=lambda x: -x.percent_change)],
        "unchanged": [asdict(c) for c in unchanged],
        "new_skills": [asdict(c) for c in new_skills],
    }


def main():
    parser = argparse.ArgumentParser(description="Compare benchmarks")
    parser.add_argument("--baseline", type=str, required=True, help="Baseline JSON")
    parser.add_argument("--candidate", type=str, required=True, help="Candidate JSON")
    parser.add_argument("--threshold", type=float, default=5.0, help="Change threshold %")
    parser.add_argument("--output", type=str, required=True, help="Output file")

    args = parser.parse_args()

    # Load files
    try:
        with open(args.baseline) as f:
            baseline = json.load(f)
            if isinstance(baseline, dict):
                baseline = baseline.get("results", [])
    except FileNotFoundError:
        print(f"Warning: Baseline not found: {args.baseline}", file=sys.stderr)
        baseline = []

    try:
        with open(args.candidate) as f:
            candidate = json.load(f)
            if isinstance(candidate, dict):
                candidate = candidate.get("results", [])
    except FileNotFoundError:
        print(f"Error: Candidate not found: {args.candidate}", file=sys.stderr)
        sys.exit(1)

    # Compare
    comparison = compare_benchmarks(baseline, candidate, args.threshold)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(comparison, f, indent=2)

    # Print summary
    summary = comparison["summary"]
    print(f"Comparison complete:", file=sys.stderr)
    print(f"  Improvements: {summary['improvements']}", file=sys.stderr)
    print(f"  Regressions:  {summary['regressions']}", file=sys.stderr)
    print(f"  Unchanged:    {summary['unchanged']}", file=sys.stderr)
    print(f"  New skills:   {summary['new_skills']}", file=sys.stderr)
    print(f"\nOutput: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
