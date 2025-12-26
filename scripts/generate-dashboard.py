#!/usr/bin/env python3
"""
Dashboard Generator

Generates an HTML dashboard from validation results.
Can be viewed locally or hosted as a GitHub Pages artifact.

Usage:
    python scripts/generate-dashboard.py \
        --test-results test-results.json \
        --validation validation-results.json \
        --benchmarks benchmarks/ \
        --output reports/dashboard.html
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def load_json(path: str) -> dict:
    """Load JSON file, return empty dict if not found."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def generate_html(
    test_results: dict,
    validation: dict,
    benchmarks: dict,
    scaling: dict,
    type_safety: dict,
) -> str:
    """Generate HTML dashboard."""

    # Calculate stats
    test_summary = test_results.get("summary", {})
    tests_passed = test_summary.get("passed", 0)
    tests_failed = test_summary.get("failed", 0)
    tests_total = tests_passed + tests_failed

    skills_total = validation.get("total_skills", 0)
    skills_valid = validation.get("valid_skills", 0)

    type_checks = type_safety.get("total_checks", 0)
    type_passed = type_safety.get("passed", 0)
    errors_caught = type_safety.get("errors_caught_at_validation", 0)

    isolated = benchmarks.get("isolated", [])
    avg_isolated = (
        sum(b.get("exec_time_mean_ms", 0) for b in isolated) / len(isolated)
        if isolated
        else 0
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skill Validation Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 2rem;
        }}
        h1 {{
            color: #58a6ff;
            margin-bottom: 0.5rem;
        }}
        .timestamp {{
            color: #8b949e;
            margin-bottom: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1.5rem;
        }}
        .card h2 {{
            font-size: 0.875rem;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        .card .value {{
            font-size: 2.5rem;
            font-weight: 600;
        }}
        .card .value.success {{ color: #3fb950; }}
        .card .value.warning {{ color: #d29922; }}
        .card .value.error {{ color: #f85149; }}
        .card .subtitle {{
            color: #8b949e;
            font-size: 0.875rem;
        }}
        .section {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .section h2 {{
            color: #58a6ff;
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid #30363d;
        }}
        th {{
            color: #8b949e;
            font-weight: 500;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        .badge.success {{ background: #238636; color: #fff; }}
        .badge.error {{ background: #da3633; color: #fff; }}
        .badge.warning {{ background: #9e6a03; color: #fff; }}
        .chart {{
            height: 200px;
            display: flex;
            align-items: flex-end;
            gap: 4px;
            padding: 1rem 0;
        }}
        .bar {{
            flex: 1;
            background: #238636;
            min-width: 20px;
            transition: height 0.3s;
        }}
        .bar:hover {{
            background: #3fb950;
        }}
        footer {{
            margin-top: 2rem;
            text-align: center;
            color: #8b949e;
            font-size: 0.875rem;
        }}
        footer a {{
            color: #58a6ff;
        }}
    </style>
</head>
<body>
    <h1>Skill Validation Dashboard</h1>
    <p class="timestamp">Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>

    <div class="grid">
        <div class="card">
            <h2>Tests</h2>
            <div class="value {'success' if tests_failed == 0 else 'error'}">{tests_passed}/{tests_total}</div>
            <div class="subtitle">{'All passing' if tests_failed == 0 else f'{tests_failed} failing'}</div>
        </div>

        <div class="card">
            <h2>Skills Validated</h2>
            <div class="value success">{skills_valid}/{skills_total}</div>
            <div class="subtitle">SKILL.md definitions</div>
        </div>

        <div class="card">
            <h2>Type Safety Checks</h2>
            <div class="value {'success' if errors_caught == 0 else 'warning'}">{type_passed}/{type_checks}</div>
            <div class="subtitle">{errors_caught} errors caught at validation</div>
        </div>

        <div class="card">
            <h2>Avg Execution Time</h2>
            <div class="value success">{avg_isolated:.2f}ms</div>
            <div class="subtitle">Isolated skill benchmark</div>
        </div>
    </div>
"""

    # Scaling section
    if scaling:
        results = scaling.get("results", [])
        width_results = sorted(
            [r for r in results if r.get("dimension") == "width"],
            key=lambda x: x["scale"],
        )
        depth_results = sorted(
            [r for r in results if r.get("dimension") == "depth"],
            key=lambda x: x["scale"],
        )

        html += """
    <div class="section">
        <h2>Composition Scaling</h2>
        <div class="grid">
            <div>
                <h3 style="color: #8b949e; margin-bottom: 1rem;">Width Scaling</h3>
                <table>
                    <tr><th>Width</th><th>Time (ms)</th><th>Overhead</th></tr>
"""
        for r in width_results:
            html += f"""
                    <tr>
                        <td>{r['scale']}</td>
                        <td>{r['exec_time_mean_ms']:.3f}</td>
                        <td>+{r['overhead_percent']:.1f}%</td>
                    </tr>
"""
        html += """
                </table>
            </div>
            <div>
                <h3 style="color: #8b949e; margin-bottom: 1rem;">Depth Scaling</h3>
                <table>
                    <tr><th>Depth</th><th>Time (ms)</th><th>Overhead</th></tr>
"""
        for r in depth_results:
            html += f"""
                    <tr>
                        <td>{r['scale']}</td>
                        <td>{r['exec_time_mean_ms']:.3f}</td>
                        <td>+{r['overhead_percent']:.1f}%</td>
                    </tr>
"""
        html += """
                </table>
            </div>
        </div>
    </div>
"""

    # Benchmark details
    if isolated:
        html += """
    <div class="section">
        <h2>Benchmark Details</h2>
        <table>
            <tr>
                <th>Skill</th>
                <th>Level</th>
                <th>Operation</th>
                <th>Mean (ms)</th>
                <th>P95 (ms)</th>
            </tr>
"""
        for b in sorted(isolated, key=lambda x: x.get("exec_time_mean_ms", 0))[:20]:
            html += f"""
            <tr>
                <td>{b.get('skill', 'unknown')}</td>
                <td><span class="badge success">{b.get('level', 'L1')}</span></td>
                <td>{b.get('operation', 'READ')}</td>
                <td>{b.get('exec_time_mean_ms', 0):.3f}</td>
                <td>{b.get('exec_time_p95_ms', 0):.3f}</td>
            </tr>
"""
        html += """
        </table>
    </div>
"""

    html += """
    <footer>
        <p>Reproduce locally: <code>python scripts/validate-all.py</code></p>
        <p><a href="https://github.com/agentskills/agentskills">View on GitHub</a></p>
    </footer>
</body>
</html>
"""

    return html


def main():
    parser = argparse.ArgumentParser(description="Generate dashboard")
    parser.add_argument("--test-results", type=str, help="Test results JSON")
    parser.add_argument("--validation", type=str, help="Validation results JSON")
    parser.add_argument("--benchmarks", type=str, help="Benchmarks directory")
    parser.add_argument("--output", type=str, default="reports/dashboard.html")

    args = parser.parse_args()

    # Load data
    test_results = load_json(args.test_results) if args.test_results else {}
    validation = load_json(args.validation) if args.validation else {}
    type_safety = load_json("type-safety-results.json")

    benchmarks = {}
    scaling = {}

    if args.benchmarks:
        bench_path = Path(args.benchmarks)
        if bench_path.exists():
            isolated_file = bench_path / "isolated-candidate.json"
            scaling_file = bench_path / "scaling-results.json"

            if isolated_file.exists():
                data = load_json(str(isolated_file))
                if isinstance(data, list):
                    benchmarks["isolated"] = data
                else:
                    benchmarks["isolated"] = data.get("results", [])

            if scaling_file.exists():
                scaling = load_json(str(scaling_file))

    # Generate HTML
    html = generate_html(test_results, validation, benchmarks, scaling, type_safety)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Dashboard written to {output_path}")


if __name__ == "__main__":
    main()
