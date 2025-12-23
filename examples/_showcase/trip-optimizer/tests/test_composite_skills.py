"""Tests for trip optimizer composite (L2) skills."""

import pytest
import re
from pathlib import Path


class TestCompositeSkillsExist:
    """Test that all expected composite skills exist."""

    def test_all_composite_skills_have_directories(self, composite_dir, composite_skills):
        """Each expected composite skill should have a directory."""
        for skill_name in composite_skills:
            skill_path = composite_dir / skill_name
            assert skill_path.exists(), f"Missing composite skill directory: {skill_name}"
            assert skill_path.is_dir(), f"Composite skill should be a directory: {skill_name}"

    def test_all_composite_skills_have_skill_md(self, composite_dir, composite_skills):
        """Each composite skill should have a SKILL.md file."""
        for skill_name in composite_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md for composite skill: {skill_name}"


class TestCompositeSkillStructure:
    """Test the structure of composite skill definitions."""

    @pytest.fixture
    def composite_skill_files(self, composite_dir, composite_skills):
        """Return list of SKILL.md paths for all composite skills."""
        return [composite_dir / name / "SKILL.md" for name in composite_skills]

    def test_composite_skills_have_yaml_frontmatter(self, composite_skill_files):
        """All composite skills should have YAML frontmatter."""
        for skill_file in composite_skill_files:
            content = skill_file.read_text()
            assert content.startswith("---"), f"Missing YAML frontmatter in {skill_file.parent.name}"

    def test_composite_skills_have_required_fields(self, composite_skill_files):
        """All composite skills should have required fields."""
        required_fields = ['name', 'description', 'level', 'operation']

        for skill_file in composite_skill_files:
            content = skill_file.read_text()
            for field in required_fields:
                assert f"{field}:" in content, f"Missing {field} in {skill_file.parent.name}"

    def test_composite_skills_are_level_2(self, composite_skill_files):
        """All composite skills should be level 2."""
        for skill_file in composite_skill_files:
            content = skill_file.read_text()
            assert "level: 2" in content, f"{skill_file.parent.name} should be level 2"

    def test_composite_skills_have_composes_field(self, composite_skill_files):
        """All composite skills should have a composes field."""
        for skill_file in composite_skill_files:
            content = skill_file.read_text()
            assert "composes:" in content, f"{skill_file.parent.name} should have composes field"


class TestCompositeSkillComposition:
    """Test the composition relationships of composite skills."""

    def test_destination_evaluate_composes_atomic_skills(self, composite_dir):
        """destination-evaluate should compose multiple atomic skills."""
        skill_file = composite_dir / "destination-evaluate" / "SKILL.md"
        content = skill_file.read_text()
        expected_composed = ["weather-fetch", "activity-search", "visa-check"]
        for skill in expected_composed:
            assert skill in content, f"destination-evaluate should compose {skill}"

    def test_destination_evaluate_composes_flight_search(self, composite_dir):
        """destination-evaluate should compose flight-search."""
        skill_file = composite_dir / "destination-evaluate" / "SKILL.md"
        content = skill_file.read_text()
        assert "flight-search" in content, "destination-evaluate should compose flight-search"

    def test_route_price_has_flight_reference(self, composite_dir):
        """route-price should reference flights."""
        skill_file = composite_dir / "route-price" / "SKILL.md"
        content = skill_file.read_text()
        assert "flight" in content.lower(), "route-price should reference flights"

    def test_feasibility_check_has_constraints(self, composite_dir):
        """feasibility-check should have constraint checking."""
        skill_file = composite_dir / "feasibility-check" / "SKILL.md"
        content = skill_file.read_text()
        has_constraints = ("constraint" in content.lower() or
                          "visa" in content.lower() or
                          "budget" in content.lower())
        assert has_constraints, "feasibility-check should have constraint checking"


class TestCompositeSkillContent:
    """Test the content quality of composite skills."""

    def test_destination_evaluate_has_scoring(self, composite_dir):
        """destination-evaluate should have scoring logic."""
        skill_file = composite_dir / "destination-evaluate" / "SKILL.md"
        content = skill_file.read_text()
        has_scoring = ("score" in content.lower() or
                      "algorithm" in content.lower() or
                      "weight" in content.lower())
        assert has_scoring, "destination-evaluate should have scoring logic"

    def test_destination_evaluate_has_quality_score_output(self, composite_dir):
        """destination-evaluate should output quality_score."""
        skill_file = composite_dir / "destination-evaluate" / "SKILL.md"
        content = skill_file.read_text()
        assert "quality_score" in content, "destination-evaluate should output quality_score"

    def test_route_price_has_cost_output(self, composite_dir):
        """route-price should have cost output."""
        skill_file = composite_dir / "route-price" / "SKILL.md"
        content = skill_file.read_text()
        has_cost = ("cost" in content.lower() or
                   "price" in content.lower() or
                   "$" in content)
        assert has_cost, "route-price should have cost output"

    def test_composite_skills_have_inputs_outputs(self, composite_dir, composite_skills):
        """All composite skills should have inputs and outputs sections."""
        for skill_name in composite_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            has_io = ("## Inputs" in content or
                     "| Parameter" in content or
                     "## Outputs" in content or
                     "| Field" in content)
            assert has_io, f"{skill_name} should have inputs/outputs documentation"


class TestCompositeSkillOperations:
    """Test operation types of composite skills."""

    def test_evaluate_skills_are_read_operation(self, composite_dir):
        """destination-evaluate should be READ operation."""
        skill_file = composite_dir / "destination-evaluate" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: READ" in content, "destination-evaluate should be READ operation"

    def test_check_skills_are_read_operation(self, composite_dir):
        """feasibility-check should be READ operation."""
        skill_file = composite_dir / "feasibility-check" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: READ" in content, "feasibility-check should be READ operation"

    def test_price_skills_are_read_operation(self, composite_dir):
        """route-price should be READ operation."""
        skill_file = composite_dir / "route-price" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: READ" in content, "route-price should be READ operation"


class TestCompositeSkillGraph:
    """Test composition graph documentation."""

    def test_destination_evaluate_has_composition_graph(self, composite_dir):
        """destination-evaluate should have composition graph."""
        skill_file = composite_dir / "destination-evaluate" / "SKILL.md"
        content = skill_file.read_text()
        has_graph = ("## Composition Graph" in content or
                    "```" in content and "L1" in content)
        assert has_graph, "destination-evaluate should document composition graph"
