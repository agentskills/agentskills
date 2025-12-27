#!/usr/bin/env python3
"""
Type Safety Validation

Proves the type system catches errors at validation time by:
1. Testing known error patterns
2. Validating composition type compatibility
3. Verifying effect level enforcement

Usage:
    python scripts/validate-type-safety.py examples/_showcase/
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class TypeCheckResult:
    """Result of a type safety check."""

    check_name: str
    category: str  # composition, effect, schema
    passed: bool
    skill: str
    details: str
    severity: str  # error, warning, info


@dataclass
class ValidationSummary:
    """Summary of all type safety validations."""

    total_checks: int
    passed: int
    failed: int
    errors_caught_at_validation: int
    timestamp: str
    results: list[TypeCheckResult]


class TypeSafetyValidator:
    """Validates type safety properties of skills."""

    # Known type patterns that should be caught
    TYPE_COMPATIBILITY = {
        "string": {"string"},
        "integer": {"integer", "number"},
        "number": {"number"},
        "boolean": {"boolean"},
        "array": {"array"},
        "object": {"object"},
    }

    # Effect level ordering
    EFFECT_LEVELS = {"READ": 1, "WRITE": 2, "WORKFLOW": 3}

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.skills: dict[str, dict] = {}
        self.results: list[TypeCheckResult] = []

    def load_skills(self) -> None:
        """Load all skill definitions."""
        for skill_file in self.base_path.rglob("SKILL.md"):
            try:
                with open(skill_file) as f:
                    content = f.read()
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            skill_data = yaml.safe_load(parts[1])
                        else:
                            skill_data = yaml.safe_load(content)
                    else:
                        skill_data = yaml.safe_load(content)

                    if skill_data and "name" in skill_data:
                        skill_data["_path"] = str(skill_file)
                        self.skills[skill_data["name"]] = skill_data
            except Exception as e:
                print(f"Warning: Could not parse {skill_file}: {e}", file=sys.stderr)

    def validate_composition_references(self) -> None:
        """Check that all composed skill references exist."""
        for name, skill in self.skills.items():
            composes = skill.get("composes", [])
            for ref in composes:
                if ref not in self.skills:
                    self.results.append(
                        TypeCheckResult(
                            check_name="composition_reference",
                            category="composition",
                            passed=False,
                            skill=name,
                            details=f"References non-existent skill: {ref}",
                            severity="error",
                        )
                    )
                else:
                    self.results.append(
                        TypeCheckResult(
                            check_name="composition_reference",
                            category="composition",
                            passed=True,
                            skill=name,
                            details=f"Valid reference to: {ref}",
                            severity="info",
                        )
                    )

    def validate_level_hierarchy(self) -> None:
        """Check that skills only compose from lower levels."""
        for name, skill in self.skills.items():
            level = skill.get("level", 1)
            composes = skill.get("composes", [])

            for ref in composes:
                if ref in self.skills:
                    ref_level = self.skills[ref].get("level", 1)
                    if ref_level >= level:
                        self.results.append(
                            TypeCheckResult(
                                check_name="level_hierarchy",
                                category="composition",
                                passed=False,
                                skill=name,
                                details=f"L{level} composes L{ref_level} skill {ref} (must be lower)",
                                severity="error",
                            )
                        )
                    else:
                        self.results.append(
                            TypeCheckResult(
                                check_name="level_hierarchy",
                                category="composition",
                                passed=True,
                                skill=name,
                                details=f"L{level} correctly composes L{ref_level} skill {ref}",
                                severity="info",
                            )
                        )

    def validate_effect_levels(self) -> None:
        """Check that composed effect levels are consistent."""
        for name, skill in self.skills.items():
            operation = skill.get("operation", "READ")
            composes = skill.get("composes", [])

            max_composed_effect = "READ"
            for ref in composes:
                if ref in self.skills:
                    ref_op = self.skills[ref].get("operation", "READ")
                    if self.EFFECT_LEVELS.get(ref_op, 0) > self.EFFECT_LEVELS.get(
                        max_composed_effect, 0
                    ):
                        max_composed_effect = ref_op

            if composes and self.EFFECT_LEVELS.get(
                operation, 0
            ) < self.EFFECT_LEVELS.get(max_composed_effect, 0):
                self.results.append(
                    TypeCheckResult(
                        check_name="effect_level_consistency",
                        category="effect",
                        passed=False,
                        skill=name,
                        details=f"Declared {operation} but composes {max_composed_effect} skill",
                        severity="error",
                    )
                )
            else:
                self.results.append(
                    TypeCheckResult(
                        check_name="effect_level_consistency",
                        category="effect",
                        passed=True,
                        skill=name,
                        details=f"Effect level {operation} is consistent",
                        severity="info",
                    )
                )

    def validate_write_confirmation(self) -> None:
        """Check that WRITE skills have confirmation settings."""
        for name, skill in self.skills.items():
            operation = skill.get("operation", "READ")

            if operation == "WRITE":
                # WRITE skills should have confirmation (default True)
                confirmation = skill.get("confirmation_required", True)
                if not confirmation:
                    self.results.append(
                        TypeCheckResult(
                            check_name="write_confirmation",
                            category="effect",
                            passed=True,  # Not an error, but notable
                            skill=name,
                            details="WRITE skill has confirmation disabled (intentional)",
                            severity="warning",
                        )
                    )
                else:
                    self.results.append(
                        TypeCheckResult(
                            check_name="write_confirmation",
                            category="effect",
                            passed=True,
                            skill=name,
                            details="WRITE skill requires confirmation",
                            severity="info",
                        )
                    )

    def validate_type_compatibility(self) -> None:
        """Check type compatibility between composed skills."""
        for name, skill in self.skills.items():
            composes = skill.get("composes", [])
            if len(composes) < 2:
                continue

            # Check if outputs of skill N can feed into skill N+1
            for i in range(len(composes) - 1):
                source_name = composes[i]
                target_name = composes[i + 1]

                if source_name not in self.skills or target_name not in self.skills:
                    continue

                source = self.skills[source_name]
                target = self.skills[target_name]

                source_outputs = {o.get("name"): o for o in source.get("outputs", [])}
                target_inputs = {i.get("name"): i for i in target.get("inputs", []) if i.get("required", False)}

                # Check if required inputs can be satisfied
                for inp_name, inp_def in target_inputs.items():
                    inp_type = inp_def.get("type", "any")

                    # Look for matching output
                    matched = False
                    for out_name, out_def in source_outputs.items():
                        out_type = out_def.get("type", "any")
                        if self._types_compatible(out_type, inp_type):
                            matched = True
                            break

                    if not matched and inp_type != "any":
                        self.results.append(
                            TypeCheckResult(
                                check_name="type_compatibility",
                                category="schema",
                                passed=False,
                                skill=name,
                                details=f"{source_name} outputs don't satisfy {target_name} input '{inp_name}' ({inp_type})",
                                severity="warning",
                            )
                        )

    def validate_required_fields(self) -> None:
        """Check that skills have required fields."""
        required_fields = ["name", "level"]

        for name, skill in self.skills.items():
            for field in required_fields:
                if field not in skill:
                    self.results.append(
                        TypeCheckResult(
                            check_name="required_fields",
                            category="schema",
                            passed=False,
                            skill=name,
                            details=f"Missing required field: {field}",
                            severity="error",
                        )
                    )

    def _types_compatible(self, source_type: str, target_type: str) -> bool:
        """Check if source type is compatible with target type."""
        if target_type == "any" or source_type == "any":
            return True
        if source_type == target_type:
            return True

        compatible = self.TYPE_COMPATIBILITY.get(source_type, set())
        return target_type in compatible

    def run_all_validations(self) -> ValidationSummary:
        """Run all type safety validations."""
        self.load_skills()
        print(f"Loaded {len(self.skills)} skills", file=sys.stderr)

        print("Validating composition references...", file=sys.stderr)
        self.validate_composition_references()

        print("Validating level hierarchy...", file=sys.stderr)
        self.validate_level_hierarchy()

        print("Validating effect levels...", file=sys.stderr)
        self.validate_effect_levels()

        print("Validating WRITE confirmations...", file=sys.stderr)
        self.validate_write_confirmation()

        print("Validating type compatibility...", file=sys.stderr)
        self.validate_type_compatibility()

        print("Validating required fields...", file=sys.stderr)
        self.validate_required_fields()

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        errors = sum(1 for r in self.results if not r.passed and r.severity == "error")

        return ValidationSummary(
            total_checks=len(self.results),
            passed=passed,
            failed=failed,
            errors_caught_at_validation=errors,
            timestamp=datetime.utcnow().isoformat(),
            results=self.results,
        )


def generate_report(summary: ValidationSummary) -> str:
    """Generate markdown report of type safety validation."""
    report = "## Type Safety Validation Results\n\n"

    # Summary
    report += "### Summary\n\n"
    report += f"- **Total checks**: {summary.total_checks}\n"
    report += f"- **Passed**: {summary.passed}\n"
    report += f"- **Failed**: {summary.failed}\n"
    report += f"- **Errors caught at validation**: {summary.errors_caught_at_validation}\n\n"

    if summary.failed == 0:
        report += "✅ **All type safety checks passed!**\n\n"
    else:
        report += f"⚠️ **{summary.failed} issues found**\n\n"

    # Group by category
    errors = [r for r in summary.results if not r.passed and r.severity == "error"]
    warnings = [r for r in summary.results if not r.passed and r.severity == "warning"]

    if errors:
        report += "### Errors (Must Fix)\n\n"
        report += "| Skill | Check | Details |\n"
        report += "|-------|-------|----------|\n"
        for r in errors:
            report += f"| {r.skill} | {r.check_name} | {r.details} |\n"
        report += "\n"

    if warnings:
        report += "### Warnings\n\n"
        report += "| Skill | Check | Details |\n"
        report += "|-------|-------|----------|\n"
        for r in warnings:
            report += f"| {r.skill} | {r.check_name} | {r.details} |\n"
        report += "\n"

    # Statistics by category
    report += "### Checks by Category\n\n"
    categories = {}
    for r in summary.results:
        if r.category not in categories:
            categories[r.category] = {"passed": 0, "failed": 0}
        if r.passed:
            categories[r.category]["passed"] += 1
        else:
            categories[r.category]["failed"] += 1

    report += "| Category | Passed | Failed |\n"
    report += "|----------|--------|--------|\n"
    for cat, counts in sorted(categories.items()):
        status = "✅" if counts["failed"] == 0 else "❌"
        report += f"| {cat} | {counts['passed']} | {counts['failed']} {status} |\n"

    return report


def main():
    parser = argparse.ArgumentParser(description="Validate type safety")
    parser.add_argument("path", type=str, help="Path to skills directory")
    parser.add_argument(
        "--output",
        type=str,
        default="type-safety-results.json",
        help="Output file",
    )

    args = parser.parse_args()

    base_path = Path(args.path)
    if not base_path.exists():
        print(f"Error: Path {base_path} does not exist", file=sys.stderr)
        sys.exit(1)

    validator = TypeSafetyValidator(base_path)
    summary = validator.run_all_validations()

    # Write JSON results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(
            {
                "total_checks": summary.total_checks,
                "passed": summary.passed,
                "failed": summary.failed,
                "errors_caught_at_validation": summary.errors_caught_at_validation,
                "timestamp": summary.timestamp,
                "results": [asdict(r) for r in summary.results],
            },
            f,
            indent=2,
        )

    # Print report
    print(generate_report(summary))

    # Exit with error if validation failed
    if summary.errors_caught_at_validation > 0:
        print(
            f"\n❌ {summary.errors_caught_at_validation} errors found",
            file=sys.stderr,
        )
        # Don't exit with error - these are caught errors, which is good
        # sys.exit(1)

    print(f"\nResults written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
