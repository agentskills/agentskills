"""Tests for agent orchestrator atomic (L1) skills."""

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

    def test_skill_registry_read_has_inputs(self, atomic_dir):
        """skill-registry-read should have inputs section."""
        skill_file = atomic_dir / "skill-registry-read" / "SKILL.md"
        content = skill_file.read_text()
        assert "## Inputs" in content or "| Parameter" in content

    def test_intent_classify_is_transform(self, atomic_dir):
        """intent-classify should be TRANSFORM operation."""
        skill_file = atomic_dir / "intent-classify" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: TRANSFORM" in content

    def test_worktree_create_is_write(self, atomic_dir):
        """worktree-create should be WRITE operation."""
        skill_file = atomic_dir / "worktree-create" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: WRITE" in content

    def test_completion_marker_set_is_write(self, atomic_dir):
        """completion-marker-set should be WRITE operation."""
        skill_file = atomic_dir / "completion-marker-set" / "SKILL.md"
        content = skill_file.read_text()
        assert "operation: WRITE" in content


class TestOrchestratorDomain:
    """Test domain-specific aspects of orchestrator skills."""

    def test_all_atomic_skills_have_orchestrator_domain(self, atomic_dir, atomic_skills):
        """All atomic skills should have agent-orchestration domain."""
        for skill_name in atomic_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "domain: agent-orchestration" in content, \
                f"{skill_name} should have agent-orchestration domain"

    def test_worktree_skills_reference_git(self, atomic_dir):
        """Worktree skills should reference git."""
        for skill_name in ["worktree-create", "worktree-merge"]:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "git" in content.lower(), f"{skill_name} should reference git"

    def test_agent_session_spawn_references_terminal(self, atomic_dir):
        """agent-session-spawn should reference terminal/tmux."""
        skill_file = atomic_dir / "agent-session-spawn" / "SKILL.md"
        content = skill_file.read_text()
        has_terminal = "tmux" in content.lower() or "terminal" in content.lower()
        assert has_terminal, "agent-session-spawn should reference terminal management"
