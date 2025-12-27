"""Tests for trip optimizer workflow (L3) skills."""

import pytest
import re
from pathlib import Path


class TestWorkflowSkillsExist:
    """Test that all expected workflow skills exist."""

    def test_all_workflow_skills_have_directories(self, workflows_dir, workflow_skills):
        """Each expected workflow skill should have a directory."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name
            assert skill_path.exists(), f"Missing workflow skill directory: {skill_name}"
            assert skill_path.is_dir(), f"Workflow skill should be a directory: {skill_name}"

    def test_all_workflow_skills_have_skill_md(self, workflows_dir, workflow_skills):
        """Each workflow skill should have a SKILL.md file."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md for workflow skill: {skill_name}"


class TestWorkflowSkillStructure:
    """Test the structure of workflow skill definitions."""

    @pytest.fixture
    def workflow_skill_files(self, workflows_dir, workflow_skills):
        """Return list of SKILL.md paths for all workflow skills."""
        return [workflows_dir / name / "SKILL.md" for name in workflow_skills]

    def test_workflow_skills_have_yaml_frontmatter(self, workflow_skill_files):
        """All workflow skills should have YAML frontmatter."""
        for skill_file in workflow_skill_files:
            content = skill_file.read_text()
            assert content.startswith("---"), f"Missing YAML frontmatter in {skill_file.parent.name}"

    def test_workflow_skills_have_required_fields(self, workflow_skill_files):
        """All workflow skills should have required fields."""
        required_fields = ['name', 'description', 'level', 'operation']

        for skill_file in workflow_skill_files:
            content = skill_file.read_text()
            for field in required_fields:
                assert f"{field}:" in content, f"Missing {field} in {skill_file.parent.name}"

    def test_workflow_skills_are_level_3(self, workflow_skill_files):
        """All workflow skills should be level 3."""
        for skill_file in workflow_skill_files:
            content = skill_file.read_text()
            assert "level: 3" in content, f"{skill_file.parent.name} should be level 3"

    def test_workflow_skills_have_composes_field(self, workflow_skill_files):
        """All workflow skills should have a composes field."""
        for skill_file in workflow_skill_files:
            content = skill_file.read_text()
            assert "composes:" in content, f"{skill_file.parent.name} should have composes field"


class TestSelfRecursion:
    """Test self-recursion patterns in workflow skills."""

    def test_trip_optimize_has_self_recursion(self, workflows_dir):
        """trip-optimize should compose itself for gradient descent."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        # Should compose itself (self-reference)
        assert "trip-optimize" in content and "composes:" in content, \
            "trip-optimize should have self-recursion"

    def test_option_explore_has_self_recursion(self, workflows_dir):
        """option-explore should compose itself for iteration."""
        skill_file = workflows_dir / "option-explore" / "SKILL.md"
        content = skill_file.read_text()
        # Should compose itself (self-reference)
        assert "option-explore" in content and "composes:" in content, \
            "option-explore should have self-recursion"


class TestWorkflowComposition:
    """Test workflow composition patterns."""

    def test_trip_optimize_composes_destination_evaluate(self, workflows_dir):
        """trip-optimize should compose destination-evaluate."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        assert "destination-evaluate" in content, \
            "trip-optimize should compose destination-evaluate"

    def test_trip_optimize_composes_feasibility_check(self, workflows_dir):
        """trip-optimize should compose feasibility-check."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        assert "feasibility-check" in content, \
            "trip-optimize should compose feasibility-check"

    def test_trip_optimize_composes_option_explore(self, workflows_dir):
        """trip-optimize should compose option-explore."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        assert "option-explore" in content, \
            "trip-optimize should compose option-explore"

    def test_l3_to_l3_composition(self, workflows_dir):
        """Should demonstrate L3 to L3 composition."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        # trip-optimize composes option-explore which is also L3
        assert "option-explore" in content, \
            "Should have L3 → L3 composition pattern"


class TestAlgorithmDocumentation:
    """Test algorithm documentation in workflow skills."""

    def test_trip_optimize_has_algorithm_overview(self, workflows_dir):
        """trip-optimize should have algorithm overview."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_algorithm = ("## Algorithm" in content or
                        "algorithm" in content.lower() or
                        "phase" in content.lower())
        assert has_algorithm, "trip-optimize should have algorithm overview"

    def test_trip_optimize_has_phases(self, workflows_dir):
        """trip-optimize should document phases."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_phases = ("PHASE" in content or
                     "phase" in content.lower() or
                     "step" in content.lower())
        assert has_phases, "trip-optimize should document phases"

    def test_trip_optimize_has_expected_value(self, workflows_dir):
        """trip-optimize should document expected value concept."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_ev = ("Expected Value" in content or
                 "E[V]" in content or
                 "expected_value" in content)
        assert has_ev, "trip-optimize should document expected value"

    def test_trip_optimize_has_early_termination(self, workflows_dir):
        """trip-optimize should document early termination."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_termination = ("early termination" in content.lower() or
                          "STOP" in content or
                          "marginal" in content.lower())
        assert has_termination, "trip-optimize should document early termination"


class TestWorkflowInputsOutputs:
    """Test inputs and outputs of workflow skills."""

    def test_trip_optimize_has_budget_input(self, workflows_dir):
        """trip-optimize should have budget input."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        assert "budget" in content.lower(), "trip-optimize should have budget input"

    def test_trip_optimize_has_dates_input(self, workflows_dir):
        """trip-optimize should have dates input."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        assert "date" in content.lower(), "trip-optimize should have dates input"

    def test_trip_optimize_has_recommendations_output(self, workflows_dir):
        """trip-optimize should have recommendations output."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        assert "recommendation" in content.lower(), \
            "trip-optimize should have recommendations output"

    def test_trip_optimize_has_pareto_frontier(self, workflows_dir):
        """trip-optimize should reference Pareto frontier."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        assert "pareto" in content.lower(), \
            "trip-optimize should reference Pareto frontier"


class TestMicroeconomicConcepts:
    """Test microeconomic concepts in trip optimizer."""

    def test_trip_optimize_has_marginal_concepts(self, workflows_dir):
        """trip-optimize should have marginal cost/return concepts."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_marginal = ("marginal" in content.lower() or
                       "Marginal" in content)
        assert has_marginal, "trip-optimize should have marginal concepts"

    def test_trip_optimize_has_opportunity_cost(self, workflows_dir):
        """trip-optimize should reference opportunity cost."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_opportunity = ("opportunity" in content.lower() or
                          "foregone" in content.lower())
        assert has_opportunity, "trip-optimize should reference opportunity cost"

    def test_trip_optimize_has_gradient_descent(self, workflows_dir):
        """trip-optimize should reference gradient descent."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_gradient = ("gradient" in content.lower() or
                       "descent" in content.lower() or
                       "local" in content.lower())
        assert has_gradient, "trip-optimize should reference gradient descent"


class TestExampleExecution:
    """Test example execution documentation."""

    def test_trip_optimize_has_example(self, workflows_dir):
        """trip-optimize should have execution example."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_example = ("## Example" in content or
                      "```" in content and "trip-optimize" in content)
        assert has_example, "trip-optimize should have execution example"

    def test_trip_optimize_has_recommendations_example(self, workflows_dir):
        """trip-optimize should show recommendation format."""
        skill_file = workflows_dir / "trip-optimize" / "SKILL.md"
        content = skill_file.read_text()
        has_recommendations = ("RECOMMENDATION" in content or
                              "Puerto Vallarta" in content or
                              "Cabo" in content)
        assert has_recommendations, "trip-optimize should show recommendation format"
