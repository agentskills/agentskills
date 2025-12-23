"""Tests for financial advisor composite (L2) skills."""

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

    def test_soa_prepare_composes_atomic_skills(self, composite_dir):
        """soa-prepare should compose multiple atomic skills."""
        skill_file = composite_dir / "soa-prepare" / "SKILL.md"
        content = skill_file.read_text()
        expected_composed = ["client-data-read", "compliance-check", "document-generate"]
        for skill in expected_composed:
            assert skill in content, f"soa-prepare should compose {skill}"

    def test_risk_profile_assess_composes_skills(self, composite_dir):
        """risk-profile-assess should compose skills."""
        skill_file = composite_dir / "risk-profile-assess" / "SKILL.md"
        content = skill_file.read_text()
        assert "composes:" in content, "risk-profile-assess should have composes field"
        # Should reference client data at minimum
        assert "client" in content.lower(), "risk-profile-assess should reference client data"

    def test_best_interests_verify_has_compliance_focus(self, composite_dir):
        """best-interests-verify should have compliance focus."""
        skill_file = composite_dir / "best-interests-verify" / "SKILL.md"
        content = skill_file.read_text()
        # Should reference compliance or best interests duty
        assert ("compliance" in content.lower() or
                "best interests" in content.lower() or
                "best_interests" in content.lower()), \
            "best-interests-verify should reference compliance"

    def test_portfolio_construct_references_risk_profile(self, composite_dir):
        """portfolio-construct should reference risk profile."""
        skill_file = composite_dir / "portfolio-construct" / "SKILL.md"
        content = skill_file.read_text()
        assert "risk" in content.lower(), "portfolio-construct should reference risk"


class TestCompositeSkillContent:
    """Test the content quality of composite skills."""

    def test_soa_prepare_has_workflow_steps(self, composite_dir):
        """soa-prepare should document workflow steps."""
        skill_file = composite_dir / "soa-prepare" / "SKILL.md"
        content = skill_file.read_text()
        # Should have workflow or steps documentation
        has_workflow = ("## Workflow" in content or
                       "workflow:" in content.lower() or
                       "steps" in content.lower())
        assert has_workflow, "soa-prepare should document workflow steps"

    def test_fee_disclosure_prepare_has_regulatory_context(self, composite_dir):
        """fee-disclosure-prepare should have regulatory context."""
        skill_file = composite_dir / "fee-disclosure-prepare" / "SKILL.md"
        content = skill_file.read_text()
        # Should reference fees and disclosure
        assert "fee" in content.lower(), "fee-disclosure-prepare should reference fees"
        has_disclosure = "disclos" in content.lower() or "regulatory" in content.lower()
        assert has_disclosure, "fee-disclosure-prepare should have disclosure/regulatory context"

    def test_composite_skills_have_inputs_outputs(self, composite_dir, composite_skills):
        """All composite skills should have inputs and outputs sections."""
        for skill_name in composite_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            # Should have some form of inputs/outputs documentation
            has_io = ("## Inputs" in content or
                     "| Parameter" in content or
                     "## Outputs" in content or
                     "| Field" in content)
            assert has_io, f"{skill_name} should have inputs/outputs documentation"


class TestCompositeSkillOperations:
    """Test operation types of composite skills."""

    def test_prepare_skills_are_write_operation(self, composite_dir):
        """Skills that 'prepare' documents should be WRITE operation."""
        prepare_skills = ["soa-prepare", "fee-disclosure-prepare"]
        for skill_name in prepare_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "operation: WRITE" in content, f"{skill_name} should be WRITE operation"

    def test_analyse_skills_are_read_operation(self, composite_dir):
        """Skills that 'analyse' or 'verify' should be READ operation."""
        analyse_skills = ["portfolio-analyse", "best-interests-verify"]
        for skill_name in analyse_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "operation: READ" in content, f"{skill_name} should be READ operation"

    def test_risk_profile_assess_is_write_operation(self, composite_dir):
        """risk-profile-assess should be WRITE (records client profile)."""
        skill_file = composite_dir / "risk-profile-assess" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: WRITE" in content, "risk-profile-assess should be WRITE operation"
