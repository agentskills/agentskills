"""Tests for financial advisor atomic (L1) skills."""

import pytest
import re
from pathlib import Path


class TestAtomicSkillsExist:
    """Test that all expected atomic skills exist."""

    def test_all_atomic_skills_have_directories(self, atomic_dir, atomic_skills):
        """Each expected atomic skill should have a directory."""
        for skill_name in atomic_skills:
            skill_path = atomic_dir / skill_name
            assert skill_path.exists(), f"Missing atomic skill directory: {skill_name}"
            assert skill_path.is_dir(), f"Atomic skill should be a directory: {skill_name}"

    def test_all_atomic_skills_have_skill_md(self, atomic_dir, atomic_skills):
        """Each atomic skill should have a SKILL.md file."""
        for skill_name in atomic_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md for atomic skill: {skill_name}"


class TestAtomicSkillStructure:
    """Test the structure of atomic skill definitions."""

    @pytest.fixture
    def atomic_skill_files(self, atomic_dir, atomic_skills):
        """Return list of SKILL.md paths for all atomic skills."""
        return [atomic_dir / name / "SKILL.md" for name in atomic_skills]

    def test_atomic_skills_have_yaml_frontmatter(self, atomic_skill_files):
        """All atomic skills should have YAML frontmatter."""
        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            assert content.startswith("---"), f"Missing YAML frontmatter in {skill_file.parent.name}"
            # Should have closing ---
            match = re.search(r'^---\n.*?\n---', content, re.DOTALL)
            assert match, f"Invalid YAML frontmatter in {skill_file.parent.name}"

    def test_atomic_skills_have_required_fields(self, atomic_skill_files):
        """All atomic skills should have required fields."""
        required_fields = ['name', 'description', 'level', 'operation']

        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            for field in required_fields:
                assert f"{field}:" in content, f"Missing {field} in {skill_file.parent.name}"

    def test_atomic_skills_are_level_1(self, atomic_skill_files):
        """All atomic skills should be level 1."""
        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            assert "level: 1" in content, f"{skill_file.parent.name} should be level 1"

    def test_atomic_skills_have_valid_operation(self, atomic_skill_files):
        """All atomic skills should have a valid operation type."""
        valid_operations = ['READ', 'WRITE', 'TRANSFORM']

        for skill_file in atomic_skill_files:
            content = skill_file.read_text()
            has_valid_op = any(f"operation: {op}" in content for op in valid_operations)
            assert has_valid_op, f"Invalid operation in {skill_file.parent.name}"


class TestAtomicSkillContent:
    """Test the content quality of atomic skills."""

    def test_client_data_read_has_tool_discovery(self, atomic_dir):
        """client-data-read should specify CRM tools."""
        skill_file = atomic_dir / "client-data-read" / "SKILL.md"
        content = skill_file.read_text()
        assert "tool_discovery:" in content, "client-data-read should have tool_discovery"
        assert "crm:" in content.lower() or "xplan" in content.lower(), "Should reference CRM tools"

    def test_compliance_check_has_read_operation(self, atomic_dir):
        """compliance-check should be READ operation."""
        skill_file = atomic_dir / "compliance-check" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: READ" in content, "compliance-check should be READ operation"

    def test_trade_execute_has_write_operation(self, atomic_dir):
        """trade-execute should be WRITE operation."""
        skill_file = atomic_dir / "trade-execute" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: WRITE" in content, "trade-execute should be WRITE operation"

    def test_kyc_verify_has_inputs(self, atomic_dir):
        """kyc-verify should have inputs section."""
        skill_file = atomic_dir / "kyc-verify" / "SKILL.md"
        content = skill_file.read_text()
        assert "## Inputs" in content or "| Parameter" in content, "kyc-verify should have inputs"

    def test_document_generate_has_outputs(self, atomic_dir):
        """document-generate should have outputs section."""
        skill_file = atomic_dir / "document-generate" / "SKILL.md"
        content = skill_file.read_text()
        assert "## Outputs" in content or "| Field" in content, "document-generate should have outputs"


class TestAtomicSkillDomain:
    """Test domain-specific aspects of financial advisor atomic skills."""

    def test_all_atomic_skills_have_financial_domain(self, atomic_dir, atomic_skills):
        """All atomic skills should have financial-advisory domain."""
        for skill_name in atomic_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            # Check for domain field or relevant domain keywords
            has_domain = ("domain:" in content or
                         "financial" in content.lower() or
                         "advisory" in content.lower())
            assert has_domain, f"{skill_name} should have financial domain context"

    def test_read_skills_are_read_operation(self, atomic_dir):
        """Skills with 'read' in name should be READ operation."""
        read_skills = ["client-data-read", "portfolio-read"]
        for skill_name in read_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "operation: READ" in content, f"{skill_name} should be READ operation"

    def test_update_skills_are_write_operation(self, atomic_dir):
        """Skills with 'update' or 'execute' in name should be WRITE operation."""
        write_skills = ["client-data-update", "trade-execute"]
        for skill_name in write_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "operation: WRITE" in content, f"{skill_name} should be WRITE operation"
