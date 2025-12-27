"""Pytest fixtures for skill validation tests."""

import pytest


@pytest.fixture
def skill_dir(tmp_path):
    """Create a temporary skill directory for testing."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    return skill_dir
