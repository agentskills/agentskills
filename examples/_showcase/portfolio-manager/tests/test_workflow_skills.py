"""Tests for Level 3 (Workflow) portfolio manager skills."""

import pytest
from pathlib import Path
import re

try:
    from skills_ref.validator import validate
    from skills_ref.parser import parse_skill
    SKILLS_REF_AVAILABLE = True
except ImportError:
    SKILLS_REF_AVAILABLE = False


# =============================================================================
# Skill Existence Tests
# =============================================================================

class TestWorkflowSkillsExist:
    """Verify all expected workflow skills exist."""

    def test_all_workflow_skills_present(self, workflows_dir, workflow_skills):
        """All expected workflow skills should have directories."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name
            assert skill_path.exists(), f"Workflow skill directory missing: {skill_name}"
            assert skill_path.is_dir(), f"Not a directory: {skill_name}"

    def test_all_workflow_skills_have_skill_md(self, workflows_dir, workflow_skills):
        """All workflow skills should have SKILL.md files."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"SKILL.md missing for: {skill_name}"


# =============================================================================
# Skill Validation Tests
# =============================================================================

@pytest.mark.skipif(not SKILLS_REF_AVAILABLE, reason="skills_ref not available")
class TestWorkflowSkillsValidate:
    """Validate workflow skills pass the validator."""

    @pytest.mark.parametrize("skill_name", [
        "portfolio-onboard",
        "rebalance-execute",
        "goal-based-review",
        "annual-portfolio-review",
    ])
    def test_skill_validates(self, workflows_dir, skill_name):
        """Each workflow skill should pass validation."""
        skill_path = workflows_dir / skill_name
        if skill_path.exists():
            errors = validate(skill_path)
            assert errors == [], f"Validation errors for {skill_name}: {errors}"


# =============================================================================
# Level 3 Property Tests
# =============================================================================

class TestWorkflowSkillLevelProperties:
    """Verify Level 3 skills have correct properties."""

    def test_all_workflows_are_level_3(self, workflows_dir, workflow_skills):
        """All workflow skills should be level 3."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                assert "level: 3" in content, f"{skill_name} should be level 3"

    def test_workflow_skills_have_operation(self, workflows_dir, workflow_skills):
        """All workflow skills should declare an operation."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                has_operation = (
                    "operation: READ" in content or
                    "operation: WRITE" in content or
                    "operation: TRANSFORM" in content
                )
                assert has_operation, f"{skill_name} should have operation declared"

    def test_workflow_skills_compose_multiple(self, workflows_dir, workflow_skills):
        """Workflow skills should compose multiple other skills."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                assert "composes:" in content, f"{skill_name} should compose other skills"
                # Count composed skills (lines starting with "  - " after composes:)
                composes_section = content.split("composes:")[1].split("\n")
                composed_count = sum(1 for line in composes_section
                                     if line.strip().startswith("-") and
                                     not line.strip().startswith("---"))
                assert composed_count >= 2, f"{skill_name} should compose at least 2 skills"


# =============================================================================
# State Machine Tests
# =============================================================================

class TestWorkflowStateMachines:
    """Verify workflow skills have proper state machines."""

    def test_workflows_have_states(self, workflows_dir, workflow_skills):
        """Workflow skills should define states."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                # Should have state machine or states section
                has_states = (
                    "state_machine" in content.lower() or
                    "states:" in content
                )
                assert has_states, f"{skill_name} should have state machine"

    def test_workflows_have_terminal_states(self, workflows_dir, workflow_skills):
        """Workflow skills should have terminal states."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                has_terminal = (
                    "terminal: true" in content or
                    "COMPLETE" in content or
                    "CANCELLED" in content
                )
                assert has_terminal, f"{skill_name} should have terminal state"


# =============================================================================
# Human Checkpoint Tests
# =============================================================================

class TestWorkflowHumanCheckpoints:
    """Verify workflows have appropriate human checkpoints."""

    def test_workflows_have_checkpoints(self, workflows_dir, workflow_skills):
        """Workflow skills should have human checkpoints."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                has_checkpoint = (
                    "human_checkpoint" in content.lower() or
                    "approval" in content.lower()
                )
                assert has_checkpoint, f"{skill_name} should have human checkpoints"


# =============================================================================
# Portfolio Onboard Workflow Tests
# =============================================================================

class TestPortfolioOnboard:
    """Tests for portfolio-onboard workflow."""

    def test_skill_exists(self, workflows_dir):
        """portfolio-onboard skill exists."""
        assert (workflows_dir / "portfolio-onboard" / "SKILL.md").exists()

    def test_composes_required_skills(self, workflows_dir):
        """portfolio-onboard composes required L1 and L2 skills."""
        content = (workflows_dir / "portfolio-onboard" / "SKILL.md").read_text()
        # Should compose key skills
        required = ["holdings-ingest", "portfolio-summarise", "risk-profile-estimate"]
        for skill in required:
            assert skill in content, f"portfolio-onboard should compose {skill}"

    def test_has_data_collection_state(self, workflows_dir):
        """portfolio-onboard has data collection state."""
        content = (workflows_dir / "portfolio-onboard" / "SKILL.md").read_text()
        assert "DATA_COLLECTION" in content or "data" in content.lower()

    def test_has_analysis_state(self, workflows_dir):
        """portfolio-onboard has analysis state."""
        content = (workflows_dir / "portfolio-onboard" / "SKILL.md").read_text()
        assert "ANALYSIS" in content or "analysis" in content.lower()

    def test_has_suitability_review(self, workflows_dir):
        """portfolio-onboard includes suitability review."""
        content = (workflows_dir / "portfolio-onboard" / "SKILL.md").read_text()
        assert "suitability" in content.lower()

    def test_produces_report(self, workflows_dir):
        """portfolio-onboard produces a report."""
        content = (workflows_dir / "portfolio-onboard" / "SKILL.md").read_text()
        assert "report" in content.lower()


# =============================================================================
# Rebalance Execute Workflow Tests
# =============================================================================

class TestRebalanceExecute:
    """Tests for rebalance-execute workflow."""

    def test_skill_exists(self, workflows_dir):
        """rebalance-execute skill exists."""
        assert (workflows_dir / "rebalance-execute" / "SKILL.md").exists()

    def test_has_monitoring_state(self, workflows_dir):
        """rebalance-execute has monitoring state."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "MONITOR" in content or "monitor" in content.lower()

    def test_has_trade_generation(self, workflows_dir):
        """rebalance-execute generates trades."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "trade" in content.lower()
        assert "TRADE_GENERATION" in content or "generate" in content.lower()

    def test_has_approval_gate(self, workflows_dir):
        """rebalance-execute has approval gate before execution."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "APPROVAL" in content or "approval" in content.lower()

    def test_has_execution_state(self, workflows_dir):
        """rebalance-execute has execution state."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "EXECUTION" in content or "execute" in content.lower()

    def test_has_verification_state(self, workflows_dir):
        """rebalance-execute has verification state."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "VERIFICATION" in content or "verify" in content.lower()

    def test_requires_approval(self, workflows_dir):
        """rebalance-execute requires approval for trades."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "requires_approval" in content.lower() or "human_checkpoint" in content.lower()


# =============================================================================
# Goal Based Review Workflow Tests
# =============================================================================

class TestGoalBasedReview:
    """Tests for goal-based-review workflow."""

    def test_skill_exists(self, workflows_dir):
        """goal-based-review skill exists."""
        assert (workflows_dir / "goal-based-review" / "SKILL.md").exists()

    def test_analyses_goal_progress(self, workflows_dir):
        """goal-based-review analyses goal progress."""
        content = (workflows_dir / "goal-based-review" / "SKILL.md").read_text()
        assert "goal" in content.lower()
        assert "progress" in content.lower()

    def test_provides_recommendations(self, workflows_dir):
        """goal-based-review provides recommendations."""
        content = (workflows_dir / "goal-based-review" / "SKILL.md").read_text()
        assert "recommend" in content.lower()

    def test_has_projection_analysis(self, workflows_dir):
        """goal-based-review projects future outcomes."""
        content = (workflows_dir / "goal-based-review" / "SKILL.md").read_text()
        assert "project" in content.lower() or "forecast" in content.lower()


# =============================================================================
# Annual Portfolio Review Workflow Tests
# =============================================================================

class TestAnnualPortfolioReview:
    """Tests for annual-portfolio-review workflow."""

    def test_skill_exists(self, workflows_dir):
        """annual-portfolio-review skill exists."""
        assert (workflows_dir / "annual-portfolio-review" / "SKILL.md").exists()

    def test_is_comprehensive(self, workflows_dir):
        """annual-portfolio-review is comprehensive."""
        content = (workflows_dir / "annual-portfolio-review" / "SKILL.md").read_text()
        # Should cover multiple areas
        areas_covered = 0
        if "performance" in content.lower():
            areas_covered += 1
        if "risk" in content.lower():
            areas_covered += 1
        if "goal" in content.lower():
            areas_covered += 1
        if "tax" in content.lower():
            areas_covered += 1
        if "compliance" in content.lower() or "ips" in content.lower():
            areas_covered += 1
        assert areas_covered >= 4, "annual-portfolio-review should cover multiple areas"

    def test_includes_performance_review(self, workflows_dir):
        """annual-portfolio-review includes performance review."""
        content = (workflows_dir / "annual-portfolio-review" / "SKILL.md").read_text()
        assert "PERFORMANCE" in content or "performance" in content.lower()

    def test_includes_forward_planning(self, workflows_dir):
        """annual-portfolio-review includes forward planning."""
        content = (workflows_dir / "annual-portfolio-review" / "SKILL.md").read_text()
        assert "forward" in content.lower() or "outlook" in content.lower() or "plan" in content.lower()

    def test_produces_full_report(self, workflows_dir):
        """annual-portfolio-review produces full report."""
        content = (workflows_dir / "annual-portfolio-review" / "SKILL.md").read_text()
        assert "report" in content.lower()
        assert "full_report" in content or "comprehensive" in content.lower()

    def test_has_action_items(self, workflows_dir):
        """annual-portfolio-review produces action items."""
        content = (workflows_dir / "annual-portfolio-review" / "SKILL.md").read_text()
        assert "action" in content.lower()


# =============================================================================
# Workflow Composition Chain Tests
# =============================================================================

class TestWorkflowCompositionChains:
    """Test that workflows correctly chain L1 and L2 skills."""

    def test_onboard_uses_summarise(self, workflows_dir, composite_dir):
        """portfolio-onboard should use portfolio-summarise."""
        content = (workflows_dir / "portfolio-onboard" / "SKILL.md").read_text()
        assert "portfolio-summarise" in content

    def test_rebalance_uses_trade_list(self, workflows_dir, composite_dir):
        """rebalance-execute should use trade-list-generate."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "trade-list-generate" in content

    def test_rebalance_uses_drift_monitor(self, workflows_dir, composite_dir):
        """rebalance-execute should use drift-monitor."""
        content = (workflows_dir / "rebalance-execute" / "SKILL.md").read_text()
        assert "drift-monitor" in content

    def test_annual_review_uses_health_report(self, workflows_dir, composite_dir):
        """annual-portfolio-review should use health-report-generate."""
        content = (workflows_dir / "annual-portfolio-review" / "SKILL.md").read_text()
        assert "health-report" in content.lower()


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestWorkflowErrorHandling:
    """Test that workflows define error handling."""

    def test_workflows_have_error_states(self, workflows_dir, workflow_skills):
        """Workflows should handle errors gracefully."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                has_error_handling = (
                    "error" in content.lower() or
                    "fail" in content.lower() or
                    "recovery" in content.lower()
                )
                assert has_error_handling, f"{skill_name} should have error handling"
