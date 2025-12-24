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
]

COMPOSITE_SKILLS = [
    "skill-discover",
    "skill-disambiguate",
    "skill-coherence-check",
    "agent-spawn-decide",
    "conflict-detect",
]

WORKFLOW_SKILLS = [
    "skill-compose",
    "worktree-isolate",
    "parallel-execute",
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
