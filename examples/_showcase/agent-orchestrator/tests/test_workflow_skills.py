"""Tests for agent orchestrator workflow (L3) skills."""

import pytest
import re
from pathlib import Path

from conftest import MCP_WORKFLOW_SKILLS


# Original orchestrator workflow skills (non-MCP)
ORCHESTRATOR_WORKFLOW_SKILLS = [
    "skill-compose",
    "worktree-isolate",
    "parallel-execute",
]


class TestWorkflowSkillsExist:
    """Test that all expected workflow skills exist."""

    def test_all_workflow_skills_have_directories(self, workflows_dir, workflow_skills):
        """Each expected workflow skill should have a directory."""
        for skill_name in workflow_skills:
            skill_path = workflows_dir / skill_name
            assert skill_path.exists(), f"Missing workflow skill directory: {skill_name}"

    def test_all_workflow_skills_have_skill_md(self, workflows_dir, workflow_skills):
        """Each workflow skill should have a SKILL.md file."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md for workflow skill: {skill_name}"


class TestWorkflowSkillStructure:
    """Test the structure of workflow skill definitions."""

    @pytest.fixture
    def orchestrator_skill_files(self, workflows_dir):
        """Return list of SKILL.md paths for orchestrator workflow skills (non-MCP)."""
        return [workflows_dir / name / "SKILL.md" for name in ORCHESTRATOR_WORKFLOW_SKILLS]

    def test_workflow_skills_are_level_3(self, workflows_dir, workflow_skills):
        """All workflow skills should be level 3."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "level: 3" in content, f"{skill_name} should be level 3"

    def test_orchestrator_workflow_skills_have_state_machine(self, orchestrator_skill_files):
        """Orchestrator workflow skills should have state_machine flag in frontmatter."""
        for skill_file in orchestrator_skill_files:
            content = skill_file.read_text()
            assert "state_machine: true" in content, \
                f"{skill_file.parent.name} should have state_machine"

    def test_mcp_workflow_skills_have_state_documentation(self, workflows_dir):
        """MCP workflow skills should document workflow states."""
        for skill_name in MCP_WORKFLOW_SKILLS:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            has_states = "## Workflow States" in content or "State" in content
            assert has_states, f"{skill_name} should document workflow states"

    def test_orchestrator_workflow_skills_have_composes(self, orchestrator_skill_files):
        """Orchestrator workflow skills should have composes field in frontmatter."""
        for skill_file in orchestrator_skill_files:
            content = skill_file.read_text()
            assert "composes:" in content, f"{skill_file.parent.name} should have composes field"

    def test_mcp_workflow_skills_have_composes_section(self, workflows_dir):
        """MCP workflow skills should have a Composes section."""
        for skill_name in MCP_WORKFLOW_SKILLS:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "## Composes" in content, f"{skill_name} should have Composes section"


class TestWorkflowStateMachine:
    """Test state machine definitions in workflow skills."""

    def test_skill_compose_has_state_machine(self, workflows_dir):
        """skill-compose should have state machine documentation."""
        skill_file = workflows_dir / "skill-compose" / "SKILL.md"
        content = skill_file.read_text()
        assert "## State Machine" in content or "State Machine" in content

    def test_worktree_isolate_has_state_machine(self, workflows_dir):
        """worktree-isolate should have state machine documentation."""
        skill_file = workflows_dir / "worktree-isolate" / "SKILL.md"
        content = skill_file.read_text()
        assert "## State Machine" in content or "State Machine" in content

    def test_parallel_execute_has_state_machine(self, workflows_dir):
        """parallel-execute should have state machine documentation."""
        skill_file = workflows_dir / "parallel-execute" / "SKILL.md"
        content = skill_file.read_text()
        assert "## State Machine" in content or "State Machine" in content


class TestSelfRecursion:
    """Test self-recursion patterns in workflow skills."""

    def test_parallel_execute_has_self_recursion(self, workflows_dir):
        """parallel-execute should compose itself for nested parallelism."""
        skill_file = workflows_dir / "parallel-execute" / "SKILL.md"
        content = skill_file.read_text()
        # Should reference itself in composes
        composes_match = re.search(r'composes:\s*\n((?:\s+-\s+\S+\n?)+)', content)
        if composes_match:
            composed_text = composes_match.group(1)
            assert "parallel-execute" in composed_text, \
                "parallel-execute should have self-recursion"


class TestWorkflowComposition:
    """Test workflow composition patterns."""

    def test_skill_compose_composes_discover(self, workflows_dir):
        """skill-compose should compose skill-discover."""
        skill_file = workflows_dir / "skill-compose" / "SKILL.md"
        content = skill_file.read_text()
        assert "skill-discover" in content

    def test_skill_compose_composes_coherence_check(self, workflows_dir):
        """skill-compose should compose skill-coherence-check."""
        skill_file = workflows_dir / "skill-compose" / "SKILL.md"
        content = skill_file.read_text()
        assert "skill-coherence-check" in content

    def test_worktree_isolate_composes_worktree_create(self, workflows_dir):
        """worktree-isolate should compose worktree-create."""
        skill_file = workflows_dir / "worktree-isolate" / "SKILL.md"
        content = skill_file.read_text()
        assert "worktree-create" in content

    def test_worktree_isolate_composes_agent_spawn(self, workflows_dir):
        """worktree-isolate should compose agent-session-spawn."""
        skill_file = workflows_dir / "worktree-isolate" / "SKILL.md"
        content = skill_file.read_text()
        assert "agent-session-spawn" in content

    def test_parallel_execute_composes_conflict_detect(self, workflows_dir):
        """parallel-execute should compose conflict-detect."""
        skill_file = workflows_dir / "parallel-execute" / "SKILL.md"
        content = skill_file.read_text()
        assert "conflict-detect" in content


class TestWorkflowContent:
    """Test the content quality of workflow skills."""

    def test_skill_compose_has_human_checkpoint(self, workflows_dir):
        """skill-compose should have human checkpoint."""
        skill_file = workflows_dir / "skill-compose" / "SKILL.md"
        content = skill_file.read_text()
        has_human = ("HUMAN" in content or
                    "human" in content.lower() or
                    "approve" in content.lower())
        assert has_human, "skill-compose should have human checkpoint"

    def test_worktree_isolate_has_error_handling(self, workflows_dir):
        """worktree-isolate should have error handling."""
        skill_file = workflows_dir / "worktree-isolate" / "SKILL.md"
        content = skill_file.read_text()
        has_errors = ("error" in content.lower() or
                     "exception" in content.lower() or
                     "failed" in content.lower())
        assert has_errors, "worktree-isolate should have error handling"

    def test_parallel_execute_has_strategies(self, workflows_dir):
        """parallel-execute should have execution strategies."""
        skill_file = workflows_dir / "parallel-execute" / "SKILL.md"
        content = skill_file.read_text()
        has_strategies = ("strateg" in content.lower() or
                         "parallel" in content.lower() or
                         "batch" in content.lower())
        assert has_strategies, "parallel-execute should have execution strategies"


class TestWorkflowOperations:
    """Test operation types of workflow skills."""

    def test_all_workflow_skills_are_write(self, workflows_dir, workflow_skills):
        """All workflow skills should be WRITE operation (create/modify)."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            content = skill_file.read_text()
            assert "operation: WRITE" in content, \
                f"{skill_name} should be WRITE operation"
