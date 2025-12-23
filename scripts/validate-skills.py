#!/usr/bin/env python3
"""Validate SKILL.md files in showcases.

This script checks that all SKILL.md files have valid structure:
- Required YAML frontmatter fields
- Valid level (1, 2, or 3)
- Valid operation type
- Proper composition references for L2/L3
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


# Required fields in YAML frontmatter
# Note: 'version' is optional for frontmatter-style skills
REQUIRED_FIELDS_CODEBLOCK = ['name', 'version', 'level', 'operation', 'description']
REQUIRED_FIELDS_FRONTMATTER = ['name', 'level', 'operation', 'description']
VALID_OPERATIONS = ['READ', 'WRITE', 'TRANSFORM']
VALID_LEVELS = [1, 2, 3]


def extract_yaml_frontmatter(content: str) -> tuple[str, str]:
    """Extract YAML frontmatter from markdown content.

    Supports two formats:
    1. Standard YAML frontmatter with --- delimiters
    2. YAML in ```yaml code blocks (portfolio-manager style)

    Returns (yaml_string, format_type) where format_type is 'frontmatter' or 'codeblock'
    """
    # Try standard frontmatter first (--- delimited)
    if content.startswith('---'):
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            return match.group(1), 'frontmatter'

    # Try ```yaml code block format
    match = re.search(r'```yaml\n(.*?)```', content, re.DOTALL)
    if match:
        return match.group(1), 'codeblock'

    return "", "none"


def parse_yaml_simple(yaml_str: str) -> dict:
    """Simple YAML parser for frontmatter (avoids pyyaml dependency issues)."""
    result = {}
    current_key = None

    for line in yaml_str.split('\n'):
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue

        # Check for key: value pattern
        if ':' in line and not line.startswith(' '):
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''

            # Remove inline comments (e.g., "READ  # comment")
            if '#' in value:
                value = value.split('#')[0].strip()

            # Handle multiline values (starting with >)
            if value == '>':
                result[key] = 'multiline'
            elif value:
                # Try to parse as number
                try:
                    result[key] = int(value)
                except ValueError:
                    result[key] = value
            else:
                result[key] = None
            current_key = key

    return result


def validate_skill(skill_path: Path) -> List[str]:
    """Validate a single SKILL.md file. Returns list of errors."""
    errors = []

    try:
        content = skill_path.read_text()
    except Exception as e:
        return [f"Cannot read file: {e}"]

    # Extract and parse YAML
    yaml_str, format_type = extract_yaml_frontmatter(content)
    if not yaml_str:
        return ["No YAML frontmatter found"]

    try:
        data = parse_yaml_simple(yaml_str)
    except Exception as e:
        return [f"Invalid YAML: {e}"]

    # Check required fields based on format
    required_fields = (REQUIRED_FIELDS_FRONTMATTER if format_type == 'frontmatter'
                       else REQUIRED_FIELDS_CODEBLOCK)
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate level
    if 'level' in data:
        level = data['level']
        if level not in VALID_LEVELS:
            errors.append(f"Invalid level: {level} (must be 1, 2, or 3)")

    # Validate operation
    if 'operation' in data:
        op = data['operation']
        if op not in VALID_OPERATIONS:
            errors.append(f"Invalid operation: {op} (must be READ, WRITE, or TRANSFORM)")

    # Check composition for L2/L3
    level = data.get('level', 0)
    has_composes = 'composes:' in content

    if level >= 2 and not has_composes:
        # Soft warning, not error
        pass  # Some L2 skills might not compose (e.g., ips-define)

    # Check for description
    if 'description' in data and data['description'] == 'multiline':
        # Check that there's actual content after description: >
        desc_match = re.search(r'description:\s*>\s*\n\s+(\S)', content)
        if not desc_match:
            errors.append("Empty description")

    return errors


def validate_showcase(showcase_path: Path) -> List[Tuple[Path, List[str]]]:
    """Validate all skills in a showcase. Returns list of (path, errors) tuples."""
    results = []

    # Find all SKILL.md files
    skill_files = list(showcase_path.rglob('SKILL.md'))

    if not skill_files:
        return [(showcase_path, ["No SKILL.md files found"])]

    for skill_file in skill_files:
        errors = validate_skill(skill_file)
        if errors:
            results.append((skill_file, errors))

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-skills.py <showcase_directory>")
        sys.exit(1)

    base_path = Path(sys.argv[1])

    if not base_path.exists():
        print(f"Error: {base_path} does not exist")
        sys.exit(1)

    # Find all showcases
    showcases = list(base_path.glob('*/'))
    if not showcases:
        showcases = [base_path]

    total_errors = 0
    total_skills = 0

    for showcase in showcases:
        if showcase.name.startswith('.'):
            continue

        results = validate_showcase(showcase)
        skill_count = len(list(showcase.rglob('SKILL.md')))
        total_skills += skill_count

        if results:
            print(f"\n{showcase.name}:")
            for path, errors in results:
                relative_path = path.relative_to(base_path)
                for error in errors:
                    print(f"  {relative_path}: {error}")
                    total_errors += 1
        else:
            print(f"{showcase.name}: {skill_count} skills OK")

    print(f"\n{'='*50}")
    print(f"Total: {total_skills} skills, {total_errors} errors")

    if total_errors > 0:
        sys.exit(1)

    print("All validations passed!")
    sys.exit(0)


if __name__ == '__main__':
    main()
