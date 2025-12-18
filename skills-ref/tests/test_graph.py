"""Tests for composition graph analysis."""

import pytest
from pathlib import Path
import tempfile

from skills_ref.graph import (
    CompositionGraph,
    CycleError,
    GraphAnalysis,
    SkillNode,
    validate_composition,
)


class TestSkillNode:
    """Tests for SkillNode dataclass."""

    def test_is_atomic(self):
        node = SkillNode(name="test", level=1)
        assert node.is_atomic is True
        assert node.is_composite is False
        assert node.is_workflow is False

    def test_is_composite(self):
        node = SkillNode(name="test", level=2)
        assert node.is_atomic is False
        assert node.is_composite is True
        assert node.is_workflow is False

    def test_is_workflow(self):
        node = SkillNode(name="test", level=3)
        assert node.is_atomic is False
        assert node.is_composite is False
        assert node.is_workflow is True

    def test_no_level(self):
        node = SkillNode(name="test")
        assert node.is_atomic is False
        assert node.is_composite is False
        assert node.is_workflow is False


class TestCycleError:
    """Tests for CycleError."""

    def test_str_representation(self):
        cycle = CycleError(cycle=["a", "b", "c", "a"])
        assert str(cycle) == "Circular dependency detected: a → b → c → a"

    def test_two_node_cycle(self):
        cycle = CycleError(cycle=["x", "y", "x"])
        assert str(cycle) == "Circular dependency detected: x → y → x"


class TestCompositionGraph:
    """Tests for CompositionGraph."""

    def test_manual_node_addition(self):
        """Test adding nodes directly without files."""
        graph = CompositionGraph()
        graph.nodes["web-search"] = SkillNode(
            name="web-search", level=1, operation="READ"
        )
        graph.nodes["pdf-save"] = SkillNode(
            name="pdf-save", level=1, operation="WRITE"
        )
        graph.nodes["research"] = SkillNode(
            name="research",
            level=2,
            operation="READ",
            composes=["web-search", "pdf-save"],
        )
        graph.edges["web-search"] = []
        graph.edges["pdf-save"] = []
        graph.edges["research"] = ["web-search", "pdf-save"]

        analysis = graph.analyze()
        assert len(analysis.nodes) == 3
        assert analysis.is_valid
        assert len(analysis.cycles) == 0

    def test_detect_simple_cycle(self):
        """Test detection of A -> B -> A cycle."""
        graph = CompositionGraph()
        graph.nodes["a"] = SkillNode(name="a", composes=["b"])
        graph.nodes["b"] = SkillNode(name="b", composes=["a"])
        graph.edges["a"] = ["b"]
        graph.edges["b"] = ["a"]

        cycles = graph.detect_cycles()
        assert len(cycles) >= 1
        # The cycle should contain both a and b
        cycle_members = set()
        for cycle in cycles:
            cycle_members.update(cycle.cycle)
        assert "a" in cycle_members
        assert "b" in cycle_members

    def test_detect_three_node_cycle(self):
        """Test detection of A -> B -> C -> A cycle."""
        graph = CompositionGraph()
        graph.nodes["a"] = SkillNode(name="a", composes=["b"])
        graph.nodes["b"] = SkillNode(name="b", composes=["c"])
        graph.nodes["c"] = SkillNode(name="c", composes=["a"])
        graph.edges["a"] = ["b"]
        graph.edges["b"] = ["c"]
        graph.edges["c"] = ["a"]

        cycles = graph.detect_cycles()
        assert len(cycles) >= 1

    def test_no_cycle_in_dag(self):
        """Test that a valid DAG has no cycles."""
        graph = CompositionGraph()
        # workflow -> composite -> atomic (valid hierarchy)
        graph.nodes["atomic"] = SkillNode(name="atomic", level=1)
        graph.nodes["composite"] = SkillNode(
            name="composite", level=2, composes=["atomic"]
        )
        graph.nodes["workflow"] = SkillNode(
            name="workflow", level=3, composes=["composite"]
        )
        graph.edges["atomic"] = []
        graph.edges["composite"] = ["atomic"]
        graph.edges["workflow"] = ["composite"]

        cycles = graph.detect_cycles()
        assert len(cycles) == 0

    def test_find_missing_dependencies(self):
        """Test detection of references to non-existent skills."""
        graph = CompositionGraph()
        graph.nodes["research"] = SkillNode(
            name="research", composes=["web-search", "nonexistent"]
        )
        graph.edges["research"] = ["web-search", "nonexistent"]

        missing = graph.find_missing_dependencies()
        assert "research" in missing
        assert "nonexistent" in missing["research"]
        # web-search is also missing because it's not in nodes
        assert "web-search" in missing["research"]

    def test_level_violations(self):
        """Test detection of level hierarchy violations."""
        graph = CompositionGraph()
        # Level 1 composing Level 2 is a violation
        graph.nodes["atomic"] = SkillNode(
            name="atomic", level=1, composes=["composite"]
        )
        graph.nodes["composite"] = SkillNode(name="composite", level=2)
        graph.edges["atomic"] = ["composite"]
        graph.edges["composite"] = []

        warnings = graph.check_level_violations()
        assert len(warnings) == 1
        assert "atomic" in warnings[0]
        assert "Level 1" in warnings[0]
        assert "composite" in warnings[0]
        assert "Level 2" in warnings[0]

    def test_no_level_violation_in_valid_hierarchy(self):
        """Test that valid hierarchy has no level violations."""
        graph = CompositionGraph()
        graph.nodes["atomic"] = SkillNode(name="atomic", level=1)
        graph.nodes["composite"] = SkillNode(
            name="composite", level=2, composes=["atomic"]
        )
        graph.edges["atomic"] = []
        graph.edges["composite"] = ["atomic"]

        warnings = graph.check_level_violations()
        assert len(warnings) == 0


class TestGraphAnalysis:
    """Tests for GraphAnalysis."""

    def test_is_valid_with_no_issues(self):
        """Test is_valid returns True when graph is clean."""
        analysis = GraphAnalysis(
            nodes={"a": SkillNode(name="a")},
            edges={"a": []},
            cycles=[],
            missing_dependencies={},
            level_violations=[],
        )
        assert analysis.is_valid is True

    def test_is_valid_with_cycles(self):
        """Test is_valid returns False when cycles exist."""
        analysis = GraphAnalysis(
            nodes={"a": SkillNode(name="a")},
            edges={"a": ["a"]},
            cycles=[CycleError(cycle=["a", "a"])],
            missing_dependencies={},
            level_violations=[],
        )
        assert analysis.is_valid is False

    def test_is_valid_with_missing_deps(self):
        """Test is_valid returns False when dependencies missing."""
        analysis = GraphAnalysis(
            nodes={"a": SkillNode(name="a", composes=["b"])},
            edges={"a": ["b"]},
            cycles=[],
            missing_dependencies={"a": ["b"]},
            level_violations=[],
        )
        assert analysis.is_valid is False

    def test_get_roots(self):
        """Test finding root nodes (not composed by others)."""
        analysis = GraphAnalysis(
            nodes={
                "root": SkillNode(name="root", composes=["child"]),
                "child": SkillNode(name="child"),
            },
            edges={"root": ["child"], "child": []},
            cycles=[],
            missing_dependencies={},
            level_violations=[],
        )
        roots = analysis.get_roots()
        assert "root" in roots
        assert "child" not in roots

    def test_get_leaves(self):
        """Test finding leaf nodes (don't compose others)."""
        analysis = GraphAnalysis(
            nodes={
                "root": SkillNode(name="root", composes=["child"]),
                "child": SkillNode(name="child"),
            },
            edges={"root": ["child"], "child": []},
            cycles=[],
            missing_dependencies={},
            level_violations=[],
        )
        leaves = analysis.get_leaves()
        assert "child" in leaves
        assert "root" not in leaves


class TestCompositionGraphWithFiles:
    """Tests for CompositionGraph with actual skill files."""

    def test_add_skill_from_file(self):
        """Test adding a skill from a SKILL.md file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "test-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: test-skill
description: A test skill
level: 1
operation: READ
---

# Test Skill
"""
            )

            graph = CompositionGraph()
            name = graph.add_skill(skill_dir)

            assert name == "test-skill"
            assert "test-skill" in graph.nodes
            assert graph.nodes["test-skill"].level == 1
            assert graph.nodes["test-skill"].operation == "READ"

    def test_add_skills_from_directory(self):
        """Test recursively adding skills from a directory tree."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create atomic skill
            atomic_dir = root / "_atomic" / "search"
            atomic_dir.mkdir(parents=True)
            (atomic_dir / "SKILL.md").write_text(
                """---
name: search
description: Search skill
level: 1
operation: READ
---
"""
            )

            # Create composite skill
            composite_dir = root / "_composite" / "research"
            composite_dir.mkdir(parents=True)
            (composite_dir / "SKILL.md").write_text(
                """---
name: research
description: Research skill
level: 2
operation: READ
composes:
  - search
---
"""
            )

            graph = CompositionGraph()
            added = graph.add_skills_from_directory(root)

            assert len(added) == 2
            assert "search" in graph.nodes
            assert "research" in graph.nodes
            assert graph.nodes["research"].composes == ["search"]


class TestToAscii:
    """Tests for ASCII tree generation."""

    def test_simple_tree(self):
        """Test ASCII output for a simple tree."""
        graph = CompositionGraph()
        graph.nodes["root"] = SkillNode(
            name="root", level=2, operation="READ", composes=["child"]
        )
        graph.nodes["child"] = SkillNode(
            name="child", level=1, operation="READ"
        )
        graph.edges["root"] = ["child"]
        graph.edges["child"] = []

        ascii_out = graph.to_ascii("root")
        assert "root" in ascii_out
        assert "child" in ascii_out
        assert "L2" in ascii_out
        assert "L1" in ascii_out


class TestToMermaid:
    """Tests for Mermaid diagram generation."""

    def test_mermaid_output(self):
        """Test Mermaid diagram generation."""
        graph = CompositionGraph()
        graph.nodes["a"] = SkillNode(name="a", level=2, composes=["b"])
        graph.nodes["b"] = SkillNode(name="b", level=1)
        graph.edges["a"] = ["b"]
        graph.edges["b"] = []

        mermaid = graph.to_mermaid()
        assert "graph TD" in mermaid
        assert "a -->" in mermaid
        assert "--> b" in mermaid


class TestValidateComposition:
    """Tests for the validate_composition convenience function."""

    def test_validate_valid_skills(self):
        """Test validation of valid skill set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create two valid skills
            skill1 = root / "skill1"
            skill1.mkdir()
            (skill1 / "SKILL.md").write_text(
                """---
name: skill1
description: First skill
level: 1
operation: READ
---
"""
            )

            skill2 = root / "skill2"
            skill2.mkdir()
            (skill2 / "SKILL.md").write_text(
                """---
name: skill2
description: Second skill
level: 2
operation: READ
composes:
  - skill1
---
"""
            )

            errors, warnings = validate_composition([root])
            assert len(errors) == 0

    def test_validate_detects_missing_dep(self):
        """Test validation catches missing dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            skill = root / "skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                """---
name: skill
description: A skill with missing dep
level: 2
operation: READ
composes:
  - nonexistent
---
"""
            )

            errors, warnings = validate_composition([skill])
            assert len(errors) == 1
            assert "nonexistent" in errors[0]
