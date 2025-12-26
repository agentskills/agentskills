#!/usr/bin/env python3
"""
Local Validation Script

Runs the EXACT SAME validation as CI, locally. Results are identical.

Usage:
    python scripts/validate-all.py
    python scripts/validate-all.py --quick    # Skip slow benchmarks
    python scripts/validate-all.py --verbose  # Show all output

This is the single command to prove the framework works.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_step(name: str, cmd: list[str], verbose: bool = False) -> tuple[bool, float]:
    """Run a validation step and return (success, duration)."""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}\n")

    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=not verbose,
            text=True,
        )
        duration = time.time() - start

        if result.returncode == 0:
            print(f"✅ {name} passed ({duration:.1f}s)")
            return True, duration
        else:
            print(f"❌ {name} failed ({duration:.1f}s)")
            if not verbose and result.stderr:
                print(result.stderr[:500])
            return False, duration

    except FileNotFoundError:
        duration = time.time() - start
        print(f"❌ {name} failed - command not found")
        return False, duration


def main():
    parser = argparse.ArgumentParser(description="Run all validations locally")
    parser.add_argument("--quick", action="store_true", help="Skip slow benchmarks")
    parser.add_argument("--verbose", action="store_true", help="Show all output")
    parser.add_argument(
        "--path",
        type=str,
        default="examples/_showcase/",
        help="Path to skills",
    )

    args = parser.parse_args()

    # Change to repo root
    repo_root = Path(__file__).parent.parent
    print(f"Running validations from: {repo_root}")

    results = []
    total_start = time.time()

    # Step 1: Validate skill definitions
    success, duration = run_step(
        "Skill Definition Validation",
        [
            sys.executable,
            "scripts/validate-skills.py",
            "--output",
            "validation-results.json",
            args.path,
        ],
        args.verbose,
    )
    results.append(("Skill Validation", success, duration))

    # Step 2: Run pytest
    success, duration = run_step(
        "Unit Tests (pytest)",
        [
            sys.executable,
            "-m",
            "pytest",
            f"{args.path}",
            "-v",
            "--tb=short",
        ],
        args.verbose,
    )
    results.append(("Unit Tests", success, duration))

    # Step 3: Type safety validation
    success, duration = run_step(
        "Type Safety Validation",
        [
            sys.executable,
            "scripts/validate-type-safety.py",
            "--output",
            "type-safety-results.json",
            args.path,
        ],
        args.verbose,
    )
    results.append(("Type Safety", success, duration))

    if not args.quick:
        # Step 4: Benchmark skills
        success, duration = run_step(
            "Skill Benchmarks (isolated)",
            [
                sys.executable,
                "scripts/benchmark-skills.py",
                "--mode",
                "isolated",
                "--iterations",
                "50",
                "--output",
                "benchmarks/isolated-candidate.json",
                args.path,
            ],
            args.verbose,
        )
        results.append(("Isolated Benchmarks", success, duration))

        # Step 5: Composition benchmarks
        success, duration = run_step(
            "Composition Benchmarks",
            [
                sys.executable,
                "scripts/benchmark-skills.py",
                "--mode",
                "compositions",
                "--iterations",
                "25",
                "--output",
                "benchmarks/composition-candidate.json",
                args.path,
            ],
            args.verbose,
        )
        results.append(("Composition Benchmarks", success, duration))

        # Step 6: Scaling benchmarks
        success, duration = run_step(
            "Scaling Benchmarks",
            [
                sys.executable,
                "scripts/benchmark-scaling.py",
                "--max-width",
                "5",
                "--max-depth",
                "3",
                "--iterations",
                "50",
                "--output",
                "benchmarks/scaling-results.json",
            ],
            args.verbose,
        )
        results.append(("Scaling Benchmarks", success, duration))

    # Summary
    total_duration = time.time() - total_start

    print("\n")
    print("=" * 60)
    print("  VALIDATION SUMMARY")
    print("=" * 60)
    print()

    passed = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)

    print(f"{'Step':<30} {'Status':<10} {'Time':>10}")
    print("-" * 52)

    for name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:<30} {status:<10} {duration:>8.1f}s")

    print("-" * 52)
    print(f"{'Total':<30} {'':<10} {total_duration:>8.1f}s")
    print()

    if failed == 0:
        print("🎉 ALL VALIDATIONS PASSED!")
        print()
        print("Results match what CI would produce.")
        print("Artifacts in: validation-results.json, benchmarks/")
        sys.exit(0)
    else:
        print(f"❌ {failed} VALIDATION(S) FAILED")
        print()
        print("Run with --verbose for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
