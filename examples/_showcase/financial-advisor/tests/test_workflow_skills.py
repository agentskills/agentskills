"""Tests for financial advisor workflow (L3) skills."""

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


class TestWorkflowStateMachine:
    """Test state machine definitions in workflow skills."""

    def test_client_onboard_has_state_machine(self, workflows_dir):
        """client-onboard should have a state machine."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        has_state_machine = ("state_machine:" in content or
                            "## State Machine" in content or
                            "PROSPECT" in content)
        assert has_state_machine, "client-onboard should have state machine"

    def test_client_onboard_has_prospect_state(self, workflows_dir):
        """client-onboard should start with PROSPECT state."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        assert "PROSPECT" in content, "client-onboard should have PROSPECT state"

    def test_client_onboard_has_active_state(self, workflows_dir):
        """client-onboard should end with ACTIVE state."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        assert "ACTIVE" in content, "client-onboard should have ACTIVE state"

    def test_workflow_has_multiple_states(self, workflows_dir, workflow_skills):
        """Workflows should have multiple states defined."""
        terminal_indicators = ['ACTIVE', 'COMPLETE', 'COMPLETED', 'DONE', 'FINISHED',
                              'CLOSED', 'DELIVERED', 'APPROVED', 'IMPLEMENTED']
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            # Should have at least one terminal state indicator
            has_terminal = any(term in content.upper() for term in terminal_indicators)
            assert has_terminal, f"{skill_name} should have terminal state"


class TestWorkflowComposition:
    """Test workflow composition patterns."""

    def test_client_onboard_composes_kyc_verify(self, workflows_dir):
        """client-onboard should compose kyc-verify."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        assert "kyc-verify" in content, "client-onboard should compose kyc-verify"

    def test_client_onboard_composes_risk_profile_assess(self, workflows_dir):
        """client-onboard should compose risk-profile-assess."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        assert "risk-profile-assess" in content, "client-onboard should compose risk-profile-assess"

    def test_advice_delivery_composes_soa(self, workflows_dir):
        """advice-delivery should reference SOA preparation."""
        skill_file = workflows_dir / "advice-delivery" / "SKILL.md"
        content = skill_file.read_text()
        has_soa = "soa" in content.lower() or "statement of advice" in content.lower()
        assert has_soa, "advice-delivery should reference SOA"

    def test_compliance_audit_has_compliance_checks(self, workflows_dir):
        """compliance-audit should reference compliance checks."""
        skill_file = workflows_dir / "compliance-audit" / "SKILL.md"
        content = skill_file.read_text()
        assert "compliance" in content.lower(), "compliance-audit should reference compliance"


class TestWorkflowContent:
    """Test the content quality of workflow skills."""

    def test_client_onboard_has_timeout_rules(self, workflows_dir):
        """client-onboard should have timeout/escalation rules."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        has_timeout = ("timeout" in content.lower() or
                      "escalat" in content.lower() or
                      "days" in content.lower())
        assert has_timeout, "client-onboard should have timeout rules"

    def test_client_onboard_has_compliance_checkpoints(self, workflows_dir):
        """client-onboard should have compliance checkpoints."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        has_checkpoints = ("checkpoint" in content.lower() or
                          "gate" in content.lower() or
                          "blocker" in content.lower())
        assert has_checkpoints, "client-onboard should have compliance checkpoints"

    def test_annual_review_has_review_context(self, workflows_dir):
        """annual-review should have review context."""
        skill_file = workflows_dir / "annual-review" / "SKILL.md"
        content = skill_file.read_text()
        assert "review" in content.lower(), "annual-review should reference review process"

    def test_portfolio_rebalance_has_trading_context(self, workflows_dir):
        """portfolio-rebalance should have trading context."""
        skill_file = workflows_dir / "portfolio-rebalance" / "SKILL.md"
        content = skill_file.read_text()
        has_trading = ("trade" in content.lower() or
                      "rebalance" in content.lower() or
                      "portfolio" in content.lower())
        assert has_trading, "portfolio-rebalance should have trading context"


class TestWorkflowInputsOutputs:
    """Test inputs and outputs of workflow skills."""

    def test_workflow_skills_have_inputs(self, workflows_dir, workflow_skills):
        """All workflow skills should have inputs section."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            has_inputs = ("## Inputs" in content or
                         "| Parameter" in content or
                         "inputs:" in content.lower())
            assert has_inputs, f"{skill_name} should have inputs section"

    def test_workflow_skills_have_outputs(self, workflows_dir, workflow_skills):
        """All workflow skills should have outputs section."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            has_outputs = ("## Outputs" in content or
                          "| Field" in content or
                          "outputs:" in content.lower())
            assert has_outputs, f"{skill_name} should have outputs section"

    def test_client_onboard_has_client_id_output(self, workflows_dir):
        """client-onboard should output client_id."""
        skill_file = workflows_dir / "client-onboard" / "SKILL.md"
        content = skill_file.read_text()
        assert "client_id" in content, "client-onboard should output client_id"
