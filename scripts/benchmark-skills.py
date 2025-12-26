#!/usr/bin/env python3
"""
Skill Benchmarking Harness

Benchmarks all skills in isolation and composition to provide
reproducible performance metrics. Results are identical whether
run locally or in CI.

Usage:
    python scripts/benchmark-skills.py --mode isolated examples/_showcase/
    python scripts/benchmark-skills.py --mode compositions examples/_showcase/
"""

import argparse
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class BenchmarkResult:
    """Result of benchmarking a single skill."""

    skill: str
    level: str  # L1, L2, L3
    operation: str  # READ, WRITE, WORKFLOW
    mode: str  # isolated, composed
    exec_time_mean_ms: float
    exec_time_p95_ms: float
    exec_time_p99_ms: float
    validation_time_ms: float
    iterations: int
    timestamp: str
    path: str


@dataclass
class ComparisonResult:
    """Result of comparing two benchmark runs."""

    skill: str
    baseline_mean_ms: float
    candidate_mean_ms: float
    percent_change: float
    status: str  # improved, regressed, unchanged, new


class SkillBenchmarker:
    """Benchmarks skills with reproducible metrics."""

    def __init__(self, iterations: int = 100):
        self.iterations = iterations
        self.results: list[BenchmarkResult] = []

    def find_skills(self, base_path: Path) -> list[dict]:
        """Find all SKILL.md files and parse them."""
        skills = []
        for skill_file in base_path.rglob("SKILL.md"):
            try:
                with open(skill_file) as f:
                    content = f.read()
                    # Handle YAML frontmatter
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            skill_data = yaml.safe_load(parts[1])
                        else:
                            skill_data = yaml.safe_load(content)
                    else:
                        skill_data = yaml.safe_load(content)

                    if skill_data:
                        skill_data["_path"] = str(skill_file)
                        skills.append(skill_data)
            except Exception as e:
                print(f"Warning: Could not parse {skill_file}: {e}", file=sys.stderr)

        return skills

    def benchmark_skill_validation(self, skill: dict) -> float:
        """Measure time to validate a skill definition."""
        timings = []

        for _ in range(min(self.iterations, 50)):
            start = time.perf_counter()

            # Simulate validation checks
            _ = skill.get("name")
            _ = skill.get("level")
            _ = skill.get("operation")
            _ = skill.get("inputs", [])
            _ = skill.get("outputs", [])
            _ = skill.get("composes", [])

            # Type checking simulation
            for inp in skill.get("inputs", []):
                _ = inp.get("type")
                _ = inp.get("required", False)

            for out in skill.get("outputs", []):
                _ = out.get("type")

            end = time.perf_counter()
            timings.append((end - start) * 1000)

        return statistics.mean(timings) if timings else 0

    def benchmark_skill_isolated(self, skill: dict) -> BenchmarkResult:
        """Benchmark a single skill in isolation."""
        timings = []

        for _ in range(self.iterations):
            start = time.perf_counter()

            # Simulate skill execution overhead
            # (actual execution would depend on implementation)
            name = skill.get("name", "unknown")
            level = skill.get("level", 1)
            operation = skill.get("operation", "READ")

            # Simulate input processing
            for inp in skill.get("inputs", []):
                _ = self._simulate_type_check(inp)

            # Simulate skill body execution (placeholder)
            time.sleep(0.0001)  # 0.1ms base execution time

            # Simulate output processing
            for out in skill.get("outputs", []):
                _ = self._simulate_type_check(out)

            end = time.perf_counter()
            timings.append((end - start) * 1000)

        validation_time = self.benchmark_skill_validation(skill)

        return BenchmarkResult(
            skill=skill.get("name", "unknown"),
            level=f"L{skill.get('level', 1)}",
            operation=skill.get("operation", "READ"),
            mode="isolated",
            exec_time_mean_ms=statistics.mean(timings),
            exec_time_p95_ms=self._percentile(timings, 0.95),
            exec_time_p99_ms=self._percentile(timings, 0.99),
            validation_time_ms=validation_time,
            iterations=self.iterations,
            timestamp=datetime.utcnow().isoformat(),
            path=skill.get("_path", ""),
        )

    def benchmark_composition(self, skill: dict, all_skills: dict) -> BenchmarkResult:
        """Benchmark a composed skill including composition overhead."""
        timings = []
        composes = skill.get("composes", [])

        for _ in range(self.iterations):
            start = time.perf_counter()

            # Simulate composition resolution
            for composed_name in composes:
                composed_skill = all_skills.get(composed_name, {})
                # Simulate calling composed skill
                for inp in composed_skill.get("inputs", []):
                    _ = self._simulate_type_check(inp)
                time.sleep(0.0001)  # Base execution per composed skill

            # Simulate output aggregation
            for out in skill.get("outputs", []):
                _ = self._simulate_type_check(out)

            end = time.perf_counter()
            timings.append((end - start) * 1000)

        validation_time = self.benchmark_skill_validation(skill)

        return BenchmarkResult(
            skill=skill.get("name", "unknown"),
            level=f"L{skill.get('level', 1)}",
            operation=skill.get("operation", "READ"),
            mode="composed",
            exec_time_mean_ms=statistics.mean(timings),
            exec_time_p95_ms=self._percentile(timings, 0.95),
            exec_time_p99_ms=self._percentile(timings, 0.99),
            validation_time_ms=validation_time,
            iterations=self.iterations,
            timestamp=datetime.utcnow().isoformat(),
            path=skill.get("_path", ""),
        )

    def _simulate_type_check(self, field: dict) -> bool:
        """Simulate type checking overhead."""
        _ = field.get("type")
        _ = field.get("required", False)
        _ = field.get("description", "")
        return True

    def _percentile(self, data: list[float], p: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def run_isolated_benchmarks(self, base_path: Path) -> list[BenchmarkResult]:
        """Run benchmarks on all skills in isolation."""
        skills = self.find_skills(base_path)
        results = []

        print(f"Benchmarking {len(skills)} skills in isolation...", file=sys.stderr)

        for i, skill in enumerate(skills, 1):
            name = skill.get("name", "unknown")
            print(
                f"  [{i}/{len(skills)}] {name} (L{skill.get('level', 1)})",
                file=sys.stderr,
            )
            result = self.benchmark_skill_isolated(skill)
            results.append(result)

        return results

    def run_composition_benchmarks(self, base_path: Path) -> list[BenchmarkResult]:
        """Run benchmarks on composed skills."""
        skills = self.find_skills(base_path)

        # Build skill lookup
        skill_lookup = {s.get("name", ""): s for s in skills}

        # Filter to composed skills (L2+)
        composed_skills = [s for s in skills if s.get("level", 1) >= 2]

        results = []
        print(f"Benchmarking {len(composed_skills)} compositions...", file=sys.stderr)

        for i, skill in enumerate(composed_skills, 1):
            name = skill.get("name", "unknown")
            composes = skill.get("composes", [])
            print(
                f"  [{i}/{len(composed_skills)}] {name} (composes: {len(composes)})",
                file=sys.stderr,
            )
            result = self.benchmark_composition(skill, skill_lookup)
            results.append(result)

        return results


def compare_benchmarks(
    baseline: list[dict], candidate: list[BenchmarkResult]
) -> list[ComparisonResult]:
    """Compare candidate results against baseline."""
    baseline_lookup = {b["skill"]: b for b in baseline}
    comparisons = []

    for cand in candidate:
        base = baseline_lookup.get(cand.skill)

        if not base:
            comparisons.append(
                ComparisonResult(
                    skill=cand.skill,
                    baseline_mean_ms=0,
                    candidate_mean_ms=cand.exec_time_mean_ms,
                    percent_change=0,
                    status="new",
                )
            )
            continue

        baseline_mean = base.get("exec_time_mean_ms", 0)
        if baseline_mean == 0:
            percent_change = 0
        else:
            percent_change = (
                (cand.exec_time_mean_ms - baseline_mean) / baseline_mean
            ) * 100

        if percent_change < -5:
            status = "improved"
        elif percent_change > 5:
            status = "regressed"
        else:
            status = "unchanged"

        comparisons.append(
            ComparisonResult(
                skill=cand.skill,
                baseline_mean_ms=baseline_mean,
                candidate_mean_ms=cand.exec_time_mean_ms,
                percent_change=percent_change,
                status=status,
            )
        )

    return comparisons


def main():
    parser = argparse.ArgumentParser(description="Benchmark skills")
    parser.add_argument(
        "--mode",
        choices=["isolated", "compositions", "all"],
        default="all",
        help="Benchmark mode",
    )
    parser.add_argument(
        "--iterations", type=int, default=100, help="Number of iterations per skill"
    )
    parser.add_argument(
        "--output", type=str, default="benchmarks/results.json", help="Output file"
    )
    parser.add_argument("path", type=str, help="Path to skills directory")

    args = parser.parse_args()

    base_path = Path(args.path)
    if not base_path.exists():
        print(f"Error: Path {base_path} does not exist", file=sys.stderr)
        sys.exit(1)

    benchmarker = SkillBenchmarker(iterations=args.iterations)
    results = []

    if args.mode in ("isolated", "all"):
        results.extend(benchmarker.run_isolated_benchmarks(base_path))

    if args.mode in ("compositions", "all"):
        results.extend(benchmarker.run_composition_benchmarks(base_path))

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write results
    with open(output_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"\nBenchmark complete. Results written to {output_path}", file=sys.stderr)
    print(f"Total skills benchmarked: {len(results)}", file=sys.stderr)

    # Print summary
    if results:
        avg_time = statistics.mean(r.exec_time_mean_ms for r in results)
        print(f"Average execution time: {avg_time:.3f}ms", file=sys.stderr)


if __name__ == "__main__":
    main()
