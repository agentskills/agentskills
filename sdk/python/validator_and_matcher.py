#!/usr/bin/env python3
"""
validator_and_matcher.py — Reference Python SDK & Schema Validator for Agent Skills Standard
"""
import os
import sys
import re
import argparse
from pathlib import Path

def validate_agent_skill(content: str) -> tuple[bool, str]:
    if not content.startswith("---"):
        return False, "Missing starting YAML frontmatter delimiter (---)"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "Unclosed YAML frontmatter delimiter (---)"
    fm = parts[1]
    name_m = re.search(r'^name:\s*([a-zA-Z0-9_-]+)', fm, re.MULTILINE)
    if not name_m:
        return False, "Invalid or missing 'name' field (must be alphanumeric with dashes/underscores)"
    desc_m = re.search(r'^description:\s*(.+)', fm, re.MULTILINE)
    if not desc_m:
        return False, "Missing 'description' field"
    return True, f"Valid Agent Skill: '{name_m.group(1)}'"

def main():
    parser = argparse.ArgumentParser(description="Agent Skills Standard Reference Validator")
    parser.add_argument("skill_file", nargs="?", default="SKILL.md", help="Path to SKILL.md")
    args = parser.parse_args()

    p = Path(args.skill_file)
    if not p.exists():
        print(f"File {p} not found. Running self-test validation...")
        sample = "---\nname: example-skill\ndescription: Sample agent skill\n---\n# Content"
        ok, msg = validate_agent_skill(sample)
        print(f"Self-test: {msg}")
        return

    content = p.read_text(encoding="utf-8", errors="replace")
    ok, msg = validate_agent_skill(content)
    print(f"Validation result: {msg}")

if __name__ == "__main__":
    main()
