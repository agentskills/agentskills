"""Pytest fixtures for cross-showcase tests."""

import pytest
from pathlib import Path


@pytest.fixture
def showcase_root():
    """Root directory for all showcases."""
    return Path(__file__).parent.parent


@pytest.fixture
def all_showcases(showcase_root):
    """All showcase directories."""
    showcases = []
    for path in showcase_root.iterdir():
        if path.is_dir() and not path.name.startswith(('.', 'tests', '_')):
            showcases.append(path)
    return sorted(showcases, key=lambda p: p.name)


@pytest.fixture
def all_skills_across_showcases(all_showcases):
    """All SKILL.md files across all showcases."""
    skills = []
    for showcase in all_showcases:
        for skill_file in showcase.rglob('SKILL.md'):
            skills.append(skill_file)
    return skills


@pytest.fixture
def skills_by_level(all_skills_across_showcases):
    """Skills organised by level across all showcases."""
    levels = {1: [], 2: [], 3: []}
    for skill_file in all_skills_across_showcases:
        content = skill_file.read_text()
        if 'level: 1' in content:
            levels[1].append(skill_file)
        elif 'level: 2' in content:
            levels[2].append(skill_file)
        elif 'level: 3' in content:
            levels[3].append(skill_file)
    return levels


@pytest.fixture
def skill_names_by_showcase(all_showcases):
    """Map of showcase name -> list of skill names."""
    result = {}
    for showcase in all_showcases:
        skills = []
        for skill_file in showcase.rglob('SKILL.md'):
            skills.append(skill_file.parent.name)
        result[showcase.name] = skills
    return result
