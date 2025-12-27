#!/usr/bin/env python3
"""Comprehensive skill linter for SKILL.md files.

Usage:
    skills-lint.py <path>           Lint all skills in path
    skills-lint.py <path> --fix     Auto-fix common issues
    skills-lint.py <path> --strict  Fail on warnings too

Exit codes:
    0 - All checks passed
    1 - Errors found
    2 - Warnings found (with --strict)
"""

import sys
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    """A linting issue found in a skill file."""
    file: Path
    line: Optional[int]
    severity: Severity
    code: str
    message: str

    def __str__(self):
        line_str = f":{self.line}" if self.line else ""
        return f"{self.file}{line_str}: {self.severity.value}[{self.code}]: {self.message}"


class SkillLinter:
    """Linter for SKILL.md files."""

    REQUIRED_FIELDS = ['name', 'level', 'operation', 'description']
    VALID_OPERATIONS = ['READ', 'WRITE', 'TRANSFORM']
    VALID_LEVELS = [1, 2, 3]
    VALID_TYPES = ['string', 'number', 'integer', 'boolean', 'array', 'object',
                   'date', 'datetime', 'enum', 'any']

    def __init__(self):
        self.issues: List[LintIssue] = []

    def add_issue(self, file: Path, line: Optional[int], severity: Severity,
                  code: str, message: str):
        """Add a linting issue."""
        self.issues.append(LintIssue(file, line, severity, code, message))

    def lint_file(self, skill_file: Path) -> List[LintIssue]:
        """Lint a single SKILL.md file."""
        self.issues = []

        try:
            content = skill_file.read_text()
            lines = content.split('\n')
        except Exception as e:
            self.add_issue(skill_file, None, Severity.ERROR, "E001",
                          f"Cannot read file: {e}")
            return self.issues

        # Extract frontmatter
        yaml_str, format_type = self._extract_frontmatter(content)
        if not yaml_str:
            self.add_issue(skill_file, 1, Severity.ERROR, "E002",
                          "No YAML frontmatter found")
            return self.issues

        # Parse YAML
        data = self._parse_yaml(yaml_str)

        # Run all checks
        self._check_required_fields(skill_file, data, format_type)
        self._check_level(skill_file, data)
        self._check_operation(skill_file, data)
        self._check_naming(skill_file, data)
        self._check_description(skill_file, data, content)
        self._check_composition(skill_file, data, content)
        self._check_schema(skill_file, content, lines)
        self._check_documentation(skill_file, content)
        self._check_formatting(skill_file, lines)

        return self.issues

    def _extract_frontmatter(self, content: str) -> tuple:
        """Extract YAML frontmatter from content."""
        # Standard frontmatter
        if content.startswith('---'):
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if match:
                return match.group(1), 'frontmatter'

        # Code block format
        match = re.search(r'```yaml\n(.*?)```', content, re.DOTALL)
        if match:
            return match.group(1), 'codeblock'

        return "", "none"

    def _parse_yaml(self, yaml_str: str) -> dict:
        """Simple YAML parser."""
        result = {}
        for line in yaml_str.split('\n'):
            line = line.rstrip()
            if not line or line.startswith('#'):
                continue
            if ':' in line and not line.startswith(' '):
                parts = line.split(':', 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ''
                if '#' in value:
                    value = value.split('#')[0].strip()
                if value == '>':
                    result[key] = 'multiline'
                elif value:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        result[key] = value
                else:
                    result[key] = None
        return result

    def _check_required_fields(self, file: Path, data: dict, format_type: str):
        """Check for required fields."""
        required = self.REQUIRED_FIELDS
        if format_type == 'codeblock':
            required = self.REQUIRED_FIELDS + ['version']

        for field in required:
            if field not in data:
                self.add_issue(file, None, Severity.ERROR, "E010",
                              f"Missing required field: {field}")

    def _check_level(self, file: Path, data: dict):
        """Check level is valid."""
        if 'level' not in data:
            return

        level = data['level']
        if level not in self.VALID_LEVELS:
            self.add_issue(file, None, Severity.ERROR, "E020",
                          f"Invalid level: {level} (must be 1, 2, or 3)")

        # Check directory matches level
        parent_name = file.parent.parent.name
        expected_dir = {1: '_atomic', 2: '_composite', 3: '_workflows'}
        if level in expected_dir and parent_name != expected_dir[level]:
            self.add_issue(file, None, Severity.WARNING, "W021",
                          f"Level {level} skill should be in {expected_dir[level]} directory")

    def _check_operation(self, file: Path, data: dict):
        """Check operation is valid."""
        if 'operation' not in data:
            return

        op = data['operation']
        if op not in self.VALID_OPERATIONS:
            self.add_issue(file, None, Severity.ERROR, "E030",
                          f"Invalid operation: {op} (must be READ, WRITE, or TRANSFORM)")

    def _check_naming(self, file: Path, data: dict):
        """Check naming conventions."""
        if 'name' not in data:
            return

        name = data['name']
        dir_name = file.parent.name

        # Name should match directory
        if name != dir_name:
            self.add_issue(file, None, Severity.WARNING, "W040",
                          f"Skill name '{name}' doesn't match directory '{dir_name}'")

        # Should be kebab-case
        if name != name.lower():
            self.add_issue(file, None, Severity.WARNING, "W041",
                          f"Skill name should be lowercase: {name}")

        if '_' in name:
            self.add_issue(file, None, Severity.WARNING, "W042",
                          f"Skill name should use hyphens not underscores: {name}")

    def _check_description(self, file: Path, data: dict, content: str):
        """Check description quality."""
        if 'description' not in data:
            return

        desc = data['description']
        if desc == 'multiline':
            # Check that multiline description has content
            match = re.search(r'description:\s*>\s*\n(\s+\S.*)', content)
            if not match:
                self.add_issue(file, None, Severity.WARNING, "W050",
                              "Multiline description appears to be empty")
        elif desc and len(desc) < 20:
            self.add_issue(file, None, Severity.WARNING, "W051",
                          "Description is very short (< 20 chars)")

    def _check_composition(self, file: Path, data: dict, content: str):
        """Check composition patterns."""
        level = data.get('level', 0)
        has_composes = 'composes:' in content

        if level == 1 and has_composes:
            # Check if it's actually composing (not just mentioning)
            if re.search(r'composes:\s*\n\s+-', content):
                self.add_issue(file, None, Severity.WARNING, "W060",
                              "Level 1 (atomic) skill should not compose other skills")

        if level >= 2 and not has_composes:
            self.add_issue(file, None, Severity.INFO, "I061",
                          "Level 2+ skill doesn't have composes field")

    def _check_schema(self, file: Path, content: str, lines: List[str]):
        """Check schema definitions."""
        has_input = 'input:' in content
        has_output = 'output:' in content

        if not has_output:
            self.add_issue(file, None, Severity.WARNING, "W070",
                          "Skill has no output schema")

        # Check for type declarations
        if has_input or has_output:
            type_matches = re.findall(r'type:\s+(\w+)', content)
            valid_types = [t for t in type_matches if t in self.VALID_TYPES]
            if not valid_types:
                self.add_issue(file, None, Severity.WARNING, "W071",
                              "Schema has no valid type declarations")

    def _check_documentation(self, file: Path, content: str):
        """Check documentation quality."""
        content_lower = content.lower()

        # Check for examples
        if 'example' not in content_lower and '```yaml' not in content:
            self.add_issue(file, None, Severity.INFO, "I080",
                          "No usage examples found")

        # Check for error handling (L3 only)
        if 'level: 3' in content:
            if 'error' not in content_lower and 'fail' not in content_lower:
                self.add_issue(file, None, Severity.INFO, "I081",
                              "Workflow has no error handling documentation")

    def _check_formatting(self, file: Path, lines: List[str]):
        """Check formatting issues."""
        for i, line in enumerate(lines):
            # Check for trailing whitespace
            if line != line.rstrip():
                self.add_issue(file, i + 1, Severity.INFO, "I090",
                              "Trailing whitespace")

            # Check for tabs
            if '\t' in line:
                self.add_issue(file, i + 1, Severity.INFO, "I091",
                              "Tab character found (use spaces)")


def main():
    parser = argparse.ArgumentParser(description='Lint SKILL.md files')
    parser.add_argument('path', help='Path to lint')
    parser.add_argument('--strict', action='store_true',
                        help='Fail on warnings too')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format')
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: {path} does not exist")
        sys.exit(1)

    # Find all SKILL.md files
    if path.is_file():
        skill_files = [path]
    else:
        skill_files = list(path.rglob('SKILL.md'))

    if not skill_files:
        print(f"No SKILL.md files found in {path}")
        sys.exit(0)

    # Lint all files
    linter = SkillLinter()
    all_issues = []

    for skill_file in sorted(skill_files):
        issues = linter.lint_file(skill_file)
        all_issues.extend(issues)

    # Count by severity
    errors = [i for i in all_issues if i.severity == Severity.ERROR]
    warnings = [i for i in all_issues if i.severity == Severity.WARNING]
    info = [i for i in all_issues if i.severity == Severity.INFO]

    # Output
    if args.format == 'json':
        import json
        print(json.dumps([{
            'file': str(i.file),
            'line': i.line,
            'severity': i.severity.value,
            'code': i.code,
            'message': i.message
        } for i in all_issues], indent=2))
    else:
        # Group by file
        by_file = {}
        for issue in all_issues:
            if issue.file not in by_file:
                by_file[issue.file] = []
            by_file[issue.file].append(issue)

        for file, issues in sorted(by_file.items()):
            print(f"\n{file.relative_to(path) if path.is_dir() else file.name}")
            for issue in issues:
                severity_sym = {'error': '✗', 'warning': '⚠', 'info': 'ℹ'}
                sym = severity_sym.get(issue.severity.value, '•')
                line_str = f":{issue.line}" if issue.line else ""
                print(f"  {sym} {line_str} [{issue.code}] {issue.message}")

        print(f"\n{'='*50}")
        print(f"Files scanned: {len(skill_files)}")
        print(f"Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(info)}")

    # Exit code
    if errors:
        sys.exit(1)
    elif warnings and args.strict:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
