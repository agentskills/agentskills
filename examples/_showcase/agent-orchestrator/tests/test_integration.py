"""Integration tests for agent orchestrator showcase.

Tests cross-cutting concerns and showcase-wide consistency.
"""

import pytest
import re
from pathlib import Path

from conftest import (
    MCP_ATOMIC_SKILLS,
    MCP_COMPOSITE_SKILLS,
    MCP_WORKFLOW_SKILLS,
)


# Original orchestrator skills (non-MCP)
ORCHESTRATOR_SKILLS = [
    "skill-registry-read",
    "skill-graph-query",
    "intent-classify",
    "worktree-create",
    "worktree-merge",
    "agent-session-spawn",
    "completion-marker-set",
    "skill-discover",
    "skill-disambiguate",
    "skill-coherence-check",
    "agent-spawn-decide",
    "conflict-detect",
    "skill-compose",
    "worktree-isolate",
    "parallel-execute",
]

MCP_SKILLS = MCP_ATOMIC_SKILLS + MCP_COMPOSITE_SKILLS + MCP_WORKFLOW_SKILLS


class TestShowcaseStructure:
    """Test overall showcase structure."""

    def test_showcase_has_readme(self, showcase_dir):
        """Showcase should have a README.md."""
        readme = showcase_dir / "README.md"
        assert readme.exists(), "Showcase should have README.md"

    def test_showcase_has_three_level_directories(self, showcase_dir):
        """Showcase should have _atomic, _composite, and _workflows directories."""
        assert (showcase_dir / "_atomic").exists(), "Missing _atomic directory"
        assert (showcase_dir / "_composite").exists(), "Missing _composite directory"
        assert (showcase_dir / "_workflows").exists(), "Missing _workflows directory"

    def test_all_skills_have_skill_md(self, all_skill_dirs):
        """All skill directories should have SKILL.md files."""
        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md in {skill_dir.name}"


class TestSkillCounts:
    """Test expected skill counts."""

    def test_atomic_skill_count(self, atomic_dir, atomic_skills):
        """Should have expected number of atomic skills."""
        actual_skills = [d.name for d in atomic_dir.iterdir()
                        if d.is_dir() and (d / "SKILL.md").exists()]
        assert len(actual_skills) >= len(atomic_skills)

    def test_composite_skill_count(self, composite_dir, composite_skills):
        """Should have expected number of composite skills."""
        actual_skills = [d.name for d in composite_dir.iterdir()
                        if d.is_dir() and (d / "SKILL.md").exists()]
        assert len(actual_skills) >= len(composite_skills)

    def test_workflow_skill_count(self, workflows_dir, workflow_skills):
        """Should have expected number of workflow skills."""
        actual_skills = [d.name for d in workflows_dir.iterdir()
                        if d.is_dir() and (d / "SKILL.md").exists()]
        assert len(actual_skills) >= len(workflow_skills)


class TestNamingConventions:
    """Test naming conventions across the showcase."""

    def test_skill_names_are_kebab_case(self, all_skill_dirs):
        """All skill directory names should be kebab-case."""
        for skill_dir in all_skill_dirs:
            name = skill_dir.name
            assert name == name.lower(), f"Skill name should be lowercase: {name}"
            assert "_" not in name, f"Skill name should use hyphens: {name}"

    def test_skill_names_match_yaml(self, all_skill_dirs):
        """Skill directory names should match YAML name field."""
        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            content = skill_file.read_text()

            name_match = re.search(r'^name:\s*(\S+)', content, re.MULTILINE)
            if name_match:
                yaml_name = name_match.group(1)
                assert yaml_name == skill_dir.name


class TestLevelConsistency:
    """Test level field consistency."""

    def test_atomic_skills_are_level_1(self, atomic_dir):
        """All skills in _atomic should be level 1."""
        for skill_dir in atomic_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                content = (skill_dir / "SKILL.md").read_text()
                assert "level: 1" in content, f"{skill_dir.name} should be level 1"

    def test_composite_skills_are_level_2(self, composite_dir):
        """All skills in _composite should be level 2."""
        for skill_dir in composite_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                content = (skill_dir / "SKILL.md").read_text()
                assert "level: 2" in content, f"{skill_dir.name} should be level 2"

    def test_workflow_skills_are_level_3(self, workflows_dir):
        """All skills in _workflows should be level 3."""
        for skill_dir in workflows_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                content = (skill_dir / "SKILL.md").read_text()
                assert "level: 3" in content, f"{skill_dir.name} should be level 3"


class TestCompositionGraph:
    """Test composition graph integrity."""

    def test_composed_skills_exist(self, all_skill_dirs, showcase_dir):
        """All composed skills should exist in the showcase."""
        all_skill_names = [d.name for d in all_skill_dirs]

        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            content = skill_file.read_text()

            composes_match = re.search(r'composes:\s*\n((?:\s+-\s+\S+\n?)+)', content)
            if composes_match:
                composed_text = composes_match.group(1)
                composed_skills = re.findall(r'-\s+(\S+)', composed_text)

                for composed in composed_skills:
                    if composed == skill_dir.name:
                        continue  # Self-recursion allowed
                    assert composed in all_skill_names, \
                        f"{skill_dir.name} composes non-existent skill: {composed}"


class TestDomainConsistency:
    """Test domain consistency for agent orchestrator."""

    def test_orchestrator_skills_have_orchestrator_domain(self, all_skill_dirs):
        """Orchestrator skills should have agent-orchestration domain."""
        for skill_dir in all_skill_dirs:
            if skill_dir.name in ORCHESTRATOR_SKILLS:
                content = (skill_dir / "SKILL.md").read_text()
                assert "domain: agent-orchestration" in content, \
                    f"{skill_dir.name} should have agent-orchestration domain"

    def test_mcp_skills_have_mcp_domain(self, all_skill_dirs):
        """MCP skills should have mcp domain."""
        for skill_dir in all_skill_dirs:
            if skill_dir.name in MCP_SKILLS:
                content = (skill_dir / "SKILL.md").read_text()
                assert "domain: mcp" in content, \
                    f"{skill_dir.name} should have mcp domain"

    def test_all_skills_have_valid_domain(self, all_skill_dirs):
        """All skills should have a valid domain."""
        valid_domains = ["agent-orchestration", "mcp", "math", "github"]
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            has_valid_domain = any(f"domain: {d}" in content for d in valid_domains)
            assert has_valid_domain, f"{skill_dir.name} should have a valid domain"


class TestMetaSkillPatterns:
    """Test meta-skill specific patterns."""

    def test_skill_discovery_pattern_exists(self, all_skill_dirs):
        """Should have skill discovery pattern."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "skill-discover" in skill_names

    def test_disambiguation_pattern_exists(self, all_skill_dirs):
        """Should have disambiguation pattern."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "skill-disambiguate" in skill_names

    def test_coherence_pattern_exists(self, all_skill_dirs):
        """Should have coherence check pattern."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "skill-coherence-check" in skill_names

    def test_parallel_execution_pattern_exists(self, all_skill_dirs):
        """Should have parallel execution pattern."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "parallel-execute" in skill_names

    def test_worktree_isolation_pattern_exists(self, all_skill_dirs):
        """Should have worktree isolation pattern."""
        skill_names = [d.name for d in all_skill_dirs]
        assert "worktree-isolate" in skill_names


class TestDocumentation:
    """Test documentation quality."""

    def test_all_skills_have_description(self, all_skill_dirs):
        """All skills should have a description (field or section)."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            # Orchestrator skills use description: field, MCP skills use ## Description section
            has_description = "description:" in content or "## Description" in content
            assert has_description, f"{skill_dir.name} missing description"

    def test_all_skills_have_usage_examples(self, all_skill_dirs):
        """All skills should have some form of usage documentation."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            has_usage = ("## Usage" in content or
                        "## Example" in content or
                        "```" in content)
            assert has_usage, f"{skill_dir.name} should have usage examples"

    def test_readme_describes_meta_skills(self, showcase_dir):
        """README should describe meta-skill concepts."""
        readme = showcase_dir / "README.md"
        content = readme.read_text()
        has_meta = ("orchestrat" in content.lower() or
                   "meta" in content.lower() or
                   "discover" in content.lower())
        assert has_meta, "README should describe orchestration concepts"
