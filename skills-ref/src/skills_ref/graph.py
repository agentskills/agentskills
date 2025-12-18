"""Composition graph analysis for Agent Skills.

This module provides tools for analyzing the composition relationships
between skills, detecting circular dependencies, and visualizing the
dependency graph.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .errors import SkillError
from .parser import find_skill_md, read_properties


@dataclass
class SkillNode:
    """A node in the composition graph."""

    name: str
    level: Optional[int] = None
    operation: Optional[str] = None
    composes: list[str] = field(default_factory=list)
    path: Optional[Path] = None

    @property
    def is_atomic(self) -> bool:
        return self.level == 1

    @property
    def is_composite(self) -> bool:
        return self.level == 2

    @property
    def is_workflow(self) -> bool:
        return self.level == 3


@dataclass
class CycleError:
    """Represents a circular dependency in the composition graph."""

    cycle: list[str]  # List of skill names forming the cycle

    def __str__(self) -> str:
        return f"Circular dependency detected: {' → '.join(self.cycle)}"


@dataclass
class GraphAnalysis:
    """Results of analyzing a composition graph."""

    nodes: dict[str, SkillNode]
    edges: dict[str, list[str]]  # skill -> list of skills it composes
    cycles: list[CycleError]
    missing_dependencies: dict[str, list[str]]  # skill -> missing deps
    level_violations: list[str]  # warnings about level hierarchy violations

    @property
    def is_valid(self) -> bool:
        """Graph is valid if there are no cycles or missing dependencies."""
        return len(self.cycles) == 0 and len(self.missing_dependencies) == 0

    def get_roots(self) -> list[str]:
        """Get skills that are not composed by any other skill."""
        composed_skills = set()
        for deps in self.edges.values():
            composed_skills.update(deps)
        return [name for name in self.nodes if name not in composed_skills]

    def get_leaves(self) -> list[str]:
        """Get skills that don't compose any other skills (atomics)."""
        return [name for name, deps in self.edges.items() if not deps]

    def get_depth(self, skill_name: str, visited: Optional[set] = None) -> int:
        """Get the maximum depth of a skill in the composition tree."""
        if visited is None:
            visited = set()

        if skill_name in visited or skill_name not in self.edges:
            return 0

        visited.add(skill_name)
        deps = self.edges.get(skill_name, [])

        if not deps:
            return 0

        return 1 + max(self.get_depth(dep, visited.copy()) for dep in deps)


class CompositionGraph:
    """Builds and analyzes the composition graph for a set of skills."""

    def __init__(self):
        self.nodes: dict[str, SkillNode] = {}
        self.edges: dict[str, list[str]] = defaultdict(list)

    def add_skill(self, skill_path: Path) -> Optional[str]:
        """Add a skill to the graph. Returns skill name or None on error."""
        try:
            props = read_properties(skill_path)
            node = SkillNode(
                name=props.name,
                level=props.level,
                operation=props.operation,
                composes=props.composes or [],
                path=skill_path,
            )
            self.nodes[props.name] = node
            self.edges[props.name] = props.composes or []
            return props.name
        except SkillError:
            return None

    def add_skills_from_directory(self, root_dir: Path) -> list[str]:
        """Recursively add all skills found under a directory."""
        added = []
        for skill_md in root_dir.rglob("SKILL.md"):
            name = self.add_skill(skill_md.parent)
            if name:
                added.append(name)
        # Also check for lowercase
        for skill_md in root_dir.rglob("skill.md"):
            name = self.add_skill(skill_md.parent)
            if name:
                added.append(name)
        return added

    def detect_cycles(self) -> list[CycleError]:
        """Detect circular dependencies in the composition graph.

        IMPORTANT: Self-recursion is explicitly ALLOWED. A skill that composes
        itself (e.g., `recursive-search` composing `recursive-search`) is a
        valid and powerful pattern that enables:

        - Divide-and-conquer algorithms with minimal code
        - Recursive tree/graph traversal
        - Dynamic parallelisation of sub-agents
        - Tail-call optimisation patterns

        This follows functional programming principles where recursion is a
        fundamental control structure. Only cycles involving DIFFERENT skills
        are flagged as errors (e.g., A → B → A).

        Uses depth-first search with three states:
        - unvisited: not yet processed
        - visiting: currently in the DFS stack (cycle if revisited)
        - visited: fully processed
        """
        cycles = []
        unvisited = set(self.nodes.keys())
        visiting = set()
        visited = set()

        def dfs(node: str, path: list[str]) -> None:
            if node in visited:
                return
            if node in visiting:
                # Found a cycle - extract the cycle portion of the path
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                # Only report if cycle involves multiple distinct skills
                # Self-recursion (single skill) is allowed
                if len(set(cycle)) > 1:
                    cycles.append(CycleError(cycle=cycle))
                return

            visiting.add(node)
            path.append(node)

            for dep in self.edges.get(node, []):
                # Skip self-references - recursion is allowed
                if dep == node:
                    continue
                if dep in self.nodes:
                    dfs(dep, path.copy())

            visiting.remove(node)
            visited.add(node)
            if node in unvisited:
                unvisited.remove(node)

        # Start DFS from each unvisited node
        while unvisited:
            start = next(iter(unvisited))
            dfs(start, [])

        return cycles

    def find_missing_dependencies(self) -> dict[str, list[str]]:
        """Find skills that reference non-existent dependencies."""
        missing = {}
        for name, deps in self.edges.items():
            missing_deps = [d for d in deps if d not in self.nodes]
            if missing_deps:
                missing[name] = missing_deps
        return missing

    def check_level_violations(self) -> list[str]:
        """Check for level hierarchy violations.

        Best practice: Level N skills should only compose Level < N skills.
        This returns warnings, not errors.
        """
        warnings = []
        for name, node in self.nodes.items():
            if node.level is None:
                continue
            for dep in node.composes:
                dep_node = self.nodes.get(dep)
                if dep_node and dep_node.level is not None:
                    if dep_node.level >= node.level:
                        warnings.append(
                            f"'{name}' (Level {node.level}) composes '{dep}' "
                            f"(Level {dep_node.level}). Higher-level skills "
                            f"should compose lower-level skills."
                        )
        return warnings

    def analyze(self) -> GraphAnalysis:
        """Perform full analysis of the composition graph."""
        return GraphAnalysis(
            nodes=dict(self.nodes),
            edges=dict(self.edges),
            cycles=self.detect_cycles(),
            missing_dependencies=self.find_missing_dependencies(),
            level_violations=self.check_level_violations(),
        )

    def to_ascii(self, root: Optional[str] = None, indent: int = 0) -> str:
        """Generate an ASCII tree representation of the graph.

        Args:
            root: Starting skill name. If None, shows all roots.
            indent: Current indentation level (for recursion).

        Returns:
            ASCII tree string.
        """
        lines = []

        if root is None:
            # Find all roots and render each
            analysis = self.analyze()
            roots = analysis.get_roots()
            if not roots:
                roots = list(self.nodes.keys())[:5]  # Show first 5 if no clear roots

            for i, r in enumerate(roots):
                if i > 0:
                    lines.append("")  # Blank line between trees
                lines.append(self.to_ascii(r, 0))
            return "\n".join(lines)

        # Render single node with its dependencies
        node = self.nodes.get(root)
        if node is None:
            return f"{'  ' * indent}[unknown: {root}]"

        level_str = f"L{node.level}" if node.level else "?"
        op_str = node.operation or "?"
        prefix = "  " * indent
        lines.append(f"{prefix}{'└── ' if indent > 0 else ''}{root} ({level_str}, {op_str})")

        for dep in node.composes:
            lines.append(self.to_ascii(dep, indent + 1))

        return "\n".join(lines)

    def to_mermaid(self) -> str:
        """Generate a Mermaid diagram of the composition graph."""
        lines = ["graph TD"]

        # Define node styles based on level
        for name, node in self.nodes.items():
            level_suffix = f"[{name}<br/>Level {node.level or '?'}]"
            if node.level == 3:
                lines.append(f"    {name}{level_suffix}")
                lines.append(f"    style {name} fill:#e1f5fe")
            elif node.level == 2:
                lines.append(f"    {name}{level_suffix}")
                lines.append(f"    style {name} fill:#fff3e0")
            elif node.level == 1:
                lines.append(f"    {name}{level_suffix}")
                lines.append(f"    style {name} fill:#e8f5e9")
            else:
                lines.append(f"    {name}[{name}]")

        # Add edges
        for name, deps in self.edges.items():
            for dep in deps:
                lines.append(f"    {name} --> {dep}")

        return "\n".join(lines)


def validate_composition(skill_dirs: list[Path]) -> tuple[list[str], list[str]]:
    """Validate composition for a list of skill directories.

    Args:
        skill_dirs: List of paths to skill directories.

    Returns:
        Tuple of (errors, warnings).
    """
    graph = CompositionGraph()

    for skill_dir in skill_dirs:
        if skill_dir.is_dir():
            if find_skill_md(skill_dir):
                graph.add_skill(skill_dir)
            else:
                # Maybe it's a root containing multiple skills
                graph.add_skills_from_directory(skill_dir)

    analysis = graph.analyze()

    errors = []
    warnings = []

    # Cycles are errors
    for cycle in analysis.cycles:
        errors.append(str(cycle))

    # Missing dependencies are errors
    for skill, missing in analysis.missing_dependencies.items():
        for dep in missing:
            errors.append(f"Skill '{skill}' composes unknown skill '{dep}'")

    # Level violations are warnings
    warnings.extend(analysis.level_violations)

    return errors, warnings
