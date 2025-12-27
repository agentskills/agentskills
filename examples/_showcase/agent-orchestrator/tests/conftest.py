"""Pytest configuration and fixtures for agent orchestrator skill tests."""

import pytest
from pathlib import Path
import sys

# Add skills-ref to path for imports
skills_ref_path = Path(__file__).parent.parent.parent.parent.parent / "skills-ref"
if str(skills_ref_path) not in sys.path:
    sys.path.insert(0, str(skills_ref_path))


@pytest.fixture
def showcase_dir():
    """Return the agent orchestrator showcase directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def atomic_dir(showcase_dir):
    """Return the atomic skills directory."""
    return showcase_dir / "_atomic"


@pytest.fixture
def composite_dir(showcase_dir):
    """Return the composite skills directory."""
    return showcase_dir / "_composite"


@pytest.fixture
def workflows_dir(showcase_dir):
    """Return the workflows directory."""
    return showcase_dir / "_workflows"


@pytest.fixture
def all_skill_dirs(showcase_dir):
    """Return all skill directories in the showcase."""
    dirs = []
    for level_dir in ["_atomic", "_composite", "_workflows"]:
        level_path = showcase_dir / level_dir
        if level_path.exists():
            for skill_dir in level_path.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    dirs.append(skill_dir)
    return dirs


# List of all expected skills by level
ATOMIC_SKILLS = [
    "skill-registry-read",
    "skill-graph-query",
    "intent-classify",
    "worktree-create",
    "worktree-merge",
    "agent-session-spawn",
    "completion-marker-set",
    # MCP atomic skills
    "mcp-server-list",
    "mcp-tools-list",
    "mcp-tool-call",
    "mcp-resources-list",
    "mcp-prompts-list",
]

COMPOSITE_SKILLS = [
    "skill-discover",
    "skill-disambiguate",
    "skill-coherence-check",
    "agent-spawn-decide",
    "conflict-detect",
    # MCP composite skills
    "mcp-tool-discover",
    "mcp-skill-map",
    "mcp-tool-retry",
    "mcp-tool-batch",
    "mcp-tool-validate",
]

WORKFLOW_SKILLS = [
    "skill-compose",
    "worktree-isolate",
    "parallel-execute",
    # MCP workflow skills
    "mcp-skill-generate",
    "mcp-reliable-execute",
]

# MCP-specific skill lists for targeted tests
MCP_ATOMIC_SKILLS = [
    "mcp-server-list",
    "mcp-tools-list",
    "mcp-tool-call",
    "mcp-resources-list",
    "mcp-prompts-list",
]

MCP_COMPOSITE_SKILLS = [
    "mcp-tool-discover",
    "mcp-skill-map",
    "mcp-tool-retry",
    "mcp-tool-batch",
    "mcp-tool-validate",
]

MCP_WORKFLOW_SKILLS = [
    "mcp-skill-generate",
    "mcp-reliable-execute",
]


@pytest.fixture
def atomic_skills():
    """Return list of expected atomic skill names."""
    return ATOMIC_SKILLS


@pytest.fixture
def composite_skills():
    """Return list of expected composite skill names."""
    return COMPOSITE_SKILLS


@pytest.fixture
def workflow_skills():
    """Return list of expected workflow skill names."""
    return WORKFLOW_SKILLS


@pytest.fixture
def mcp_atomic_skills():
    """Return list of MCP atomic skill names."""
    return MCP_ATOMIC_SKILLS


@pytest.fixture
def mcp_composite_skills():
    """Return list of MCP composite skill names."""
    return MCP_COMPOSITE_SKILLS


@pytest.fixture
def mcp_workflow_skills():
    """Return list of MCP workflow skill names."""
    return MCP_WORKFLOW_SKILLS


@pytest.fixture
def all_mcp_skills():
    """Return all MCP skill names."""
    return MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS
