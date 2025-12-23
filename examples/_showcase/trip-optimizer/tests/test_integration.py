"""Integration tests for trip optimizer showcase.

Tests cross-cutting concerns and showcase-wide consistency.
"""

import pytest
import re
from pathlib import Path


class TestShowcaseStructure:
    """Test overall showcase structure."""

    def test_showcase_has_readme(self, showcase_dir):
        """Showcase should have a README.md."""
        readme = showcase_dir / "README.md"
        assert readme.exists(), "Showcase should have README.md"

    def test_showcase_has_three_level_directories(self, showcase_dir):
        """Showcase should have _atomic, _composite, and _workflows directories."""
        assert (showcase_dir / "_atomic").exists(), "Missing _atomic directory"
        assert (showcase_dir / "_composite").exists(), "Missing _composite directory"
        assert (showcase_dir / "_workflows").exists(), "Missing _workflows directory"

    def test_all_skills_have_skill_md(self, all_skill_dirs):
        """All skill directories should have SKILL.md files."""
        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md in {skill_dir.name}"


class TestSkillCounts:
    """Test expected skill counts."""

    def test_atomic_skill_count(self, atomic_dir, atomic_skills):
        """Should have expected number of atomic skills."""
        actual_skills = [d.name for d in atomic_dir.iterdir()
                        if d.is_dir() and (d / "SKILL.md").exists()]
        assert len(actual_skills) >= len(atomic_skills), \
            f"Expected at least {len(atomic_skills)} atomic skills, found {len(actual_skills)}"

    def test_composite_skill_count(self, composite_dir, composite_skills):
        """Should have expected number of composite skills."""
        actual_skills = [d.name for d in composite_dir.iterdir()
                        if d.is_dir() and (d / "SKILL.md").exists()]
        assert len(actual_skills) >= len(composite_skills), \
            f"Expected at least {len(composite_skills)} composite skills, found {len(actual_skills)}"

    def test_workflow_skill_count(self, workflows_dir, workflow_skills):
        """Should have expected number of workflow skills."""
        actual_skills = [d.name for d in workflows_dir.iterdir()
                        if d.is_dir() and (d / "SKILL.md").exists()]
        assert len(actual_skills) >= len(workflow_skills), \
            f"Expected at least {len(workflow_skills)} workflow skills, found {len(actual_skills)}"


class TestNamingConventions:
    """Test naming conventions across the showcase."""

    def test_skill_names_are_kebab_case(self, all_skill_dirs):
        """All skill directory names should be kebab-case."""
        for skill_dir in all_skill_dirs:
            name = skill_dir.name
            assert name == name.lower(), f"Skill name should be lowercase: {name}"
            assert "_" not in name, f"Skill name should use hyphens, not underscores: {name}"

    def test_skill_names_match_yaml(self, all_skill_dirs):
        """Skill directory names should match YAML name field."""
        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            content = skill_file.read_text()

            name_match = re.search(r'^name:\s*(\S+)', content, re.MULTILINE)
            if name_match:
                yaml_name = name_match.group(1)
                assert yaml_name == skill_dir.name, \
                    f"Directory name '{skill_dir.name}' doesn't match YAML name '{yaml_name}'"


class TestLevelConsistency:
    """Test level field consistency."""

    def test_atomic_skills_are_level_1(self, atomic_dir):
        """All skills in _atomic should be level 1."""
        for skill_dir in atomic_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                content = (skill_dir / "SKILL.md").read_text()
                assert "level: 1" in content, f"{skill_dir.name} should be level 1"

    def test_composite_skills_are_level_2(self, composite_dir):
        """All skills in _composite should be level 2."""
        for skill_dir in composite_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                content = (skill_dir / "SKILL.md").read_text()
                assert "level: 2" in content, f"{skill_dir.name} should be level 2"

    def test_workflow_skills_are_level_3(self, workflows_dir):
        """All skills in _workflows should be level 3."""
        for skill_dir in workflows_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                content = (skill_dir / "SKILL.md").read_text()
                assert "level: 3" in content, f"{skill_dir.name} should be level 3"


class TestCompositionGraph:
    """Test composition graph integrity."""

    def test_composed_skills_exist(self, all_skill_dirs, showcase_dir):
        """All composed skills should exist in the showcase."""
        all_skill_names = [d.name for d in all_skill_dirs]

        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            content = skill_file.read_text()

            composes_match = re.search(r'composes:\s*\n((?:\s+-\s+\S+\n?)+)', content)
            if composes_match:
                composed_text = composes_match.group(1)
                composed_skills = re.findall(r'-\s+(\S+)', composed_text)

                for composed in composed_skills:
                    # Skip self-references
                    if composed == skill_dir.name:
                        continue
                    # Check skill exists
                    assert composed in all_skill_names, \
                        f"{skill_dir.name} composes non-existent skill: {composed}"


class TestOperationConsistency:
    """Test operation type consistency."""

    def test_all_skills_have_valid_operation(self, all_skill_dirs):
        """All skills should have a valid operation type."""
        valid_operations = ['READ', 'WRITE', 'TRANSFORM']

        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            content = skill_file.read_text()

            assert "operation:" in content, f"{skill_dir.name} missing operation field"

            has_valid_op = any(f"operation: {op}" in content for op in valid_operations)
            assert has_valid_op, f"{skill_dir.name} has invalid operation type"

    def test_trip_optimizer_is_read_heavy(self, all_skill_dirs):
        """Trip optimizer should be primarily READ operations."""
        read_count = 0
        total_count = len(all_skill_dirs)

        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "operation: READ" in content:
                read_count += 1

        # Trip optimizer should be mostly READ (research-heavy)
        assert read_count >= total_count * 0.8, \
            f"Trip optimizer should be READ-heavy, found {read_count}/{total_count}"


class TestAdvancedPatterns:
    """Test advanced composable skills patterns."""

    def test_fan_out_parallelization(self, workflows_dir):
        """trip-optimize should document fan-out parallelization."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_fanout = ("fan-out" in content.lower() or
                     "parallel" in content.lower() or
                     "simultaneously" in content.lower())
        assert has_fanout, "trip-optimize should document fan-out parallelization"

    def test_self_recursion_documented(self, workflows_dir):
        """Self-recursion should be documented."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_recursion = ("self-recurs" in content.lower() or
                        "Self-recurs" in content or
                        "recursive" in content.lower())
        assert has_recursion, "Self-recursion should be documented"

    def test_l3_to_l3_documented(self, workflows_dir):
        """L3 → L3 composition should be documented."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_l3l3 = ("L3 → L3" in content or
                   "L3 to L3" in content.lower() or
                   "option-explore" in content)
        assert has_l3l3, "L3 → L3 composition should be documented"


class TestDocumentation:
    """Test documentation quality."""

    def test_all_skills_have_description(self, all_skill_dirs):
        """All skills should have a description field."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            assert "description:" in content, f"{skill_dir.name} missing description"

    def test_all_skills_have_usage_examples(self, all_skill_dirs):
        """All skills should have some form of usage documentation."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            has_usage = ("## Usage" in content or
                        "## Example" in content or
                        "```" in content)
            assert has_usage, f"{skill_dir.name} should have usage examples"

    def test_readme_describes_showcase(self, showcase_dir):
        """README should describe the trip optimizer showcase."""
        readme = showcase_dir / "README.md"
        content = readme.read_text()
        has_description = ("trip" in content.lower() or
                          "travel" in content.lower() or
                          "optimizer" in content.lower())
        assert has_description, "README should describe trip optimizer"


class TestTravelDomain:
    """Test travel domain coverage."""

    def test_covers_flight_booking(self, all_skill_dirs):
        """Should have flight-related skills."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "flight-search" in skill_names, "Should have flight-search skill"

    def test_covers_hotel_booking(self, all_skill_dirs):
        """Should have hotel-related skills."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "hotel-search" in skill_names, "Should have hotel-search skill"

    def test_covers_weather(self, all_skill_dirs):
        """Should have weather-related skills."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "weather-fetch" in skill_names, "Should have weather-fetch skill"

    def test_covers_visa_requirements(self, all_skill_dirs):
        """Should have visa-related skills."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "visa-check" in skill_names, "Should have visa-check skill"

    def test_covers_activities(self, all_skill_dirs):
        """Should have activity-related skills."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "activity-search" in skill_names, "Should have activity-search skill"
