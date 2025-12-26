#!/usr/bin/env python3
"""
Generate Markdown Report for PR Comments

Combines test results, validation results, and benchmarks into
a single markdown report suitable for GitHub PR comments.

Usage:
    python scripts/generate-report.py \
        --test-results test-results.json \
        --validation validation-results.json \
        --benchmarks benchmarks/ \
        --output reports/summary.md
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_json(path: str) -> dict:
    """Load JSON file, return empty dict if not found."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def generate_test_section(test_results: dict) -> str:
    """Generate test results section."""
    if not test_results:
        return "### Test Results\n\n⚠️ No test results available\n\n"

    summary = test_results.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    total = summary.get("total", passed + failed)

    section = "### Test Results\n\n"

    if failed == 0:
        section += f"✅ **All {total} tests passed**\n\n"
    else:
        section += f"❌ **{failed}/{total} tests failed**\n\n"

        # List failures
        failures = test_results.get("tests", [])
        failed_tests = [t for t in failures if t.get("outcome") == "failed"]

        if failed_tests:
            section += "| Test | Error |\n"
            section += "|------|-------|\n"
            for test in failed_tests[:10]:  # Limit to 10
                name = test.get("nodeid", "unknown")
                # Truncate long names
                if len(name) > 60:
                    name = "..." + name[-57:]
                error = test.get("call", {}).get("crash", {}).get("message", "")[:50]
                section += f"| {name} | {error} |\n"

            if len(failed_tests) > 10:
                section += f"\n*...and {len(failed_tests) - 10} more failures*\n"

    return section + "\n"


def generate_validation_section(validation_results: dict) -> str:
    """Generate validation results section."""
    if not validation_results:
        return "### Skill Validation\n\n⚠️ No validation results available\n\n"

    total = validation_results.get("total_skills", 0)
    valid = validation_results.get("valid_skills", 0)
    invalid = validation_results.get("invalid_skills", 0)

    section = "### Skill Validation\n\n"

    if invalid == 0:
        section += f"✅ **All {total} skills valid**\n\n"
    else:
        section += f"⚠️ **{invalid}/{total} skills have issues**\n\n"

    # Summary stats
    section += f"- Total skills: {total}\n"
    section += f"- Valid: {valid}\n"
    section += f"- Invalid: {invalid}\n\n"

    return section


def generate_type_safety_section(type_safety: dict) -> str:
    """Generate type safety section."""
    if not type_safety:
        return "### Type Safety\n\n⚠️ No type safety results available\n\n"

    total = type_safety.get("total_checks", 0)
    passed = type_safety.get("passed", 0)
    errors = type_safety.get("errors_caught_at_validation", 0)

    section = "### Type Safety Validation\n\n"

    section += f"- **Checks run**: {total}\n"
    section += f"- **Passed**: {passed}\n"
    section += f"- **Errors caught at validation time**: {errors}\n\n"

    if errors > 0:
        section += f"✅ **{errors} potential runtime errors caught at validation**\n\n"
    else:
        section += "✅ **No type errors detected**\n\n"

    return section


def generate_benchmark_section(benchmarks: dict, comparison: dict) -> str:
    """Generate benchmark results section."""
    section = "### Performance Benchmarks\n\n"

    if not benchmarks:
        section += "⚠️ No benchmark results available\n\n"
        return section

    # Isolated benchmarks
    isolated = benchmarks.get("isolated", [])
    if isolated:
        avg_time = sum(b.get("exec_time_mean_ms", 0) for b in isolated) / len(isolated)
        section += f"**Isolated Skills**: {len(isolated)} benchmarked, "
        section += f"avg {avg_time:.3f}ms\n\n"

    # Composition benchmarks
    compositions = benchmarks.get("compositions", [])
    if compositions:
        avg_time = sum(b.get("exec_time_mean_ms", 0) for b in compositions) / len(compositions)
        section += f"**Compositions**: {len(compositions)} benchmarked, "
        section += f"avg {avg_time:.3f}ms\n\n"

    # Comparison with baseline
    if comparison:
        improvements = comparison.get("improvements", [])
        regressions = comparison.get("regressions", [])

        if regressions:
            section += f"⚠️ **{len(regressions)} performance regressions detected**\n\n"
            section += "| Skill | Change | Before | After |\n"
            section += "|-------|--------|--------|-------|\n"
            for reg in regressions[:5]:
                section += f"| {reg['skill']} | "
                section += f"+{reg['percent_change']:.1f}% | "
                section += f"{reg['baseline_mean_ms']:.2f}ms | "
                section += f"{reg['candidate_mean_ms']:.2f}ms |\n"
            section += "\n"

        if improvements:
            section += f"✅ **{len(improvements)} performance improvements**\n\n"

        if not regressions and not improvements:
            section += "✅ **No significant performance changes**\n\n"

    return section


def generate_scaling_section(scaling: dict) -> str:
    """Generate scaling benchmark section."""
    if not scaling:
        return ""

    section = "### Composition Scaling\n\n"

    results = scaling.get("results", [])
    width_results = [r for r in results if r.get("dimension") == "width"]
    depth_results = [r for r in results if r.get("dimension") == "depth"]

    if width_results:
        first = min(width_results, key=lambda x: x["scale"])
        last = max(width_results, key=lambda x: x["scale"])
        ratio = last["exec_time_mean_ms"] / first["exec_time_mean_ms"]

        section += f"- **Width scaling** (1→{last['scale']}): {ratio:.1f}x time\n"
        if ratio <= last["scale"] * 1.2:
            section += "  - ✅ Linear scaling\n"

    if depth_results:
        first = min(depth_results, key=lambda x: x["scale"])
        last = max(depth_results, key=lambda x: x["scale"])
        ratio = last["exec_time_mean_ms"] / first["exec_time_mean_ms"]

        section += f"- **Depth scaling** (0→{last['scale']}): {ratio:.1f}x time\n"
        if ratio <= (last["scale"] + 1) * 1.5:
            section += "  - ✅ Linear scaling\n"

    return section + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate validation report")
    parser.add_argument("--test-results", type=str, help="Test results JSON")
    parser.add_argument("--validation", type=str, help="Validation results JSON")
    parser.add_argument("--benchmarks", type=str, help="Benchmarks directory")
    parser.add_argument("--comparison", type=str, help="Comparison results JSON")
    parser.add_argument("--output", type=str, default="reports/summary.md")

    args = parser.parse_args()

    # Load all data
    test_results = load_json(args.test_results) if args.test_results else {}
    validation = load_json(args.validation) if args.validation else {}

    benchmarks = {}
    comparison = {}
    scaling = {}

    if args.benchmarks:
        bench_path = Path(args.benchmarks)
        if bench_path.exists():
            isolated_file = bench_path / "isolated-candidate.json"
            comp_file = bench_path / "composition-candidate.json"
            scaling_file = bench_path / "scaling-results.json"

            if isolated_file.exists():
                benchmarks["isolated"] = load_json(str(isolated_file))
            if comp_file.exists():
                benchmarks["compositions"] = load_json(str(comp_file))
            if scaling_file.exists():
                scaling = load_json(str(scaling_file))

    if args.comparison:
        comparison = load_json(args.comparison)

    # Load type safety results
    type_safety = load_json("type-safety-results.json")

    # Generate report
    report = "## ✅ Skill Validation Results\n\n"
    report += f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"

    report += generate_test_section(test_results)
    report += generate_validation_section(validation)
    report += generate_type_safety_section(type_safety)
    report += generate_benchmark_section(benchmarks, comparison)
    report += generate_scaling_section(scaling)

    # Summary
    report += "---\n\n"
    report += "**Reproduce locally**: `python scripts/validate-all.py`\n\n"
    report += "[View detailed artifacts](../../actions/runs/${{ github.run_id }})\n"

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(report)

    print(report)
    print(f"\nReport written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
