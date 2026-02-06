#!/usr/bin/env python3
"""
Compose Validator Skill - Check if two skills can be composed.

Uses the skills_ref.composition module for validation logic.
No duplicated code - single source of truth.

Usage:
    python run.py --source slack-search --target slack-read
    python run.py --source slack-search --target slack-summarize --json
"""

import argparse
import json
import sys
from pathlib import Path


def get_skills_directory() -> Path:
    """Get the skills directory (parent of this skill's directory)."""
    return Path(__file__).parent.parent.parent


def find_skill(skill_ref: str, skills_dir: Path) -> Path:
    """Find a skill by name or path."""
    skill_path = Path(skill_ref)
    if skill_path.exists():
        return skill_path

    skill_dir = skills_dir / skill_ref
    if skill_dir.exists():
        return skill_dir

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Validate that two skills can be composed together"
    )
    parser.add_argument("--source", "-s", required=True,
                        help="Source skill name or path")
    parser.add_argument("--target", "-t", required=True,
                        help="Target skill name or path")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    # Try to import from installed package
    try:
        from skills_ref.composition import check_composition
    except ImportError:
        print("Error: skills_ref package not installed.", file=sys.stderr)
        print("Install with: pip install -e /path/to/skills-ref", file=sys.stderr)
        sys.exit(1)

    skills_dir = get_skills_directory()

    # Find skills
    source_dir = find_skill(args.source, skills_dir)
    target_dir = find_skill(args.target, skills_dir)

    if not source_dir:
        result = {
            "valid": False,
            "source": args.source,
            "target": args.target,
            "reason": f"Source skill not found: {args.source}",
        }
    elif not target_dir:
        result = {
            "valid": False,
            "source": args.source,
            "target": args.target,
            "reason": f"Target skill not found: {args.target}",
        }
    else:
        # Use the composition module (single source of truth)
        comp_result = check_composition(source_dir, target_dir)
        result = {
            "valid": comp_result.valid,
            "source": comp_result.source,
            "target": comp_result.target,
            "reason": comp_result.reason,
        }
        if comp_result.matched_type:
            result["matched_type"] = comp_result.matched_type

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["valid"]:
            print(f"✓ {result['source']} → {result['target']}")
            print(f"  {result['reason']}")
        else:
            print(f"✗ {result['source']} → {result['target']}")
            print(f"  {result['reason']}")

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
