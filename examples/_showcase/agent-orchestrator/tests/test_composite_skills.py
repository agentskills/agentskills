"""Tests for agent orchestrator composite (L2) skills."""

import pytest
import re
from pathlib import Path

from conftest import MCP_COMPOSITE_SKILLS


# Original orchestrator composite skills (non-MCP)
ORCHESTRATOR_COMPOSITE_SKILLS = [
    "skill-discover",
    "skill-disambiguate",
    "skill-coherence-check",
    "agent-spawn-decide",
    "conflict-detect",
]


class TestCompositeSkillsExist:
    """Test that all expected composite skills exist."""

    def test_all_composite_skills_have_directories(self, composite_dir, composite_skills):
        """Each expected composite skill should have a directory."""
        for skill_name in composite_skills:
            skill_path = composite_dir / skill_name
            assert skill_path.exists(), f"Missing composite skill directory: {skill_name}"

    def test_all_composite_skills_have_skill_md(self, composite_dir, composite_skills):
        """Each composite skill should have a SKILL.md file."""
        for skill_name in composite_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md for composite skill: {skill_name}"


class TestCompositeSkillStructure:
    """Test the structure of composite skill definitions."""

    @pytest.fixture
    def orchestrator_skill_files(self, composite_dir):
        """Return list of SKILL.md paths for orchestrator composite skills (non-MCP)."""
        return [composite_dir / name / "SKILL.md" for name in ORCHESTRATOR_COMPOSITE_SKILLS]

    def test_composite_skills_are_level_2(self, composite_dir, composite_skills):
        """All composite skills should be level 2."""
        for skill_name in composite_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "level: 2" in content, f"{skill_name} should be level 2"

    def test_orchestrator_composite_skills_have_composes_field(self, orchestrator_skill_files):
        """Orchestrator composite skills should have a composes field in frontmatter."""
        for skill_file in orchestrator_skill_files:
            content = skill_file.read_text()
            assert "composes:" in content, f"{skill_file.parent.name} should have composes field"

    def test_mcp_composite_skills_have_composes_section(self, composite_dir):
        """MCP composite skills should have a Composes section."""
        for skill_name in MCP_COMPOSITE_SKILLS:
            skill_file = composite_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "## Composes" in content, f"{skill_name} should have Composes section"


class TestCompositeSkillComposition:
    """Test the composition relationships of composite skills."""

    def test_skill_discover_composes_intent_classify(self, composite_dir):
        """skill-discover should compose intent-classify."""
        skill_file = composite_dir / "skill-discover" / "SKILL.md"
        content = skill_file.read_text()
        assert "intent-classify" in content, "skill-discover should compose intent-classify"

    def test_skill_discover_composes_skill_registry_read(self, composite_dir):
        """skill-discover should compose skill-registry-read."""
        skill_file = composite_dir / "skill-discover" / "SKILL.md"
        content = skill_file.read_text()
        assert "skill-registry-read" in content

    def test_skill_disambiguate_composes_intent_classify(self, composite_dir):
        """skill-disambiguate should compose intent-classify."""
        skill_file = composite_dir / "skill-disambiguate" / "SKILL.md"
        content = skill_file.read_text()
        assert "intent-classify" in content

    def test_skill_coherence_check_composes_graph_query(self, composite_dir):
        """skill-coherence-check should compose skill-graph-query."""
        skill_file = composite_dir / "skill-coherence-check" / "SKILL.md"
        content = skill_file.read_text()
        assert "skill-graph-query" in content

    def test_agent_spawn_decide_composes_skill_registry(self, composite_dir):
        """agent-spawn-decide should compose skill-registry-read."""
        skill_file = composite_dir / "agent-spawn-decide" / "SKILL.md"
        content = skill_file.read_text()
        assert "skill-registry-read" in content


class TestCompositeSkillContent:
    """Test the content quality of composite skills."""

    def test_skill_discover_has_intent_matching(self, composite_dir):
        """skill-discover should document intent matching."""
        skill_file = composite_dir / "skill-discover" / "SKILL.md"
        content = skill_file.read_text()
        assert "intent" in content.lower()

    def test_skill_disambiguate_has_ambiguity_types(self, composite_dir):
        """skill-disambiguate should document ambiguity types."""
        skill_file = composite_dir / "skill-disambiguate" / "SKILL.md"
        content = skill_file.read_text()
        assert "ambiguity" in content.lower() or "ambiguous" in content.lower()

    def test_skill_coherence_check_has_validation_rules(self, composite_dir):
        """skill-coherence-check should have validation rules."""
        skill_file = composite_dir / "skill-coherence-check" / "SKILL.md"
        content = skill_file.read_text()
        has_rules = "rule" in content.lower() or "validation" in content.lower()
        assert has_rules

    def test_conflict_detect_has_conflict_types(self, composite_dir):
        """conflict-detect should document conflict types."""
        skill_file = composite_dir / "conflict-detect" / "SKILL.md"
        content = skill_file.read_text()
        assert "conflict" in content.lower()


class TestCompositeSkillOperations:
    """Test operation types of composite skills."""

    def test_orchestrator_composite_skills_are_read(self, composite_dir):
        """Orchestrator composite skills should be READ operation (analysis only)."""
        for skill_name in ORCHESTRATOR_COMPOSITE_SKILLS:
            skill_file = composite_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "operation: READ" in content, \
                f"{skill_name} should be READ operation"

    def test_mcp_composite_skills_have_valid_operations(self, composite_dir):
        """MCP composite skills should have valid operation types."""
        valid_operations = ['READ', 'WRITE', 'TRANSFORM']
        for skill_name in MCP_COMPOSITE_SKILLS:
            skill_file = composite_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            has_valid_op = any(f"operation: {op}" in content for op in valid_operations)
            assert has_valid_op, f"Invalid operation in {skill_name}"
