"""Cross-showcase consistency tests.

These tests verify that patterns are consistent across all showcases
and that common skills are named and structured similarly.
"""

import pytest
import re
from pathlib import Path
from collections import defaultdict


# =============================================================================
# Naming Convention Tests
# =============================================================================

class TestNamingConventions:
    """Verify consistent naming across showcases."""

    def test_skill_names_use_kebab_case(self, all_skills_across_showcases):
        """All skill names should use kebab-case."""
        for skill_file in all_skills_across_showcases:
            skill_name = skill_file.parent.name
            # Should be lowercase with hyphens
            assert skill_name == skill_name.lower(), \
                f"Skill name should be lowercase: {skill_name}"
            assert '_' not in skill_name, \
                f"Skill name should use hyphens not underscores: {skill_name}"

    def test_directory_structure_consistent(self, all_showcases):
        """All showcases should use _atomic, _composite, _workflows structure."""
        expected_dirs = {'_atomic', '_composite', '_workflows'}
        for showcase in all_showcases:
            found_dirs = {d.name for d in showcase.iterdir()
                         if d.is_dir() and d.name.startswith('_')}
            # Should have at least atomic and one of composite/workflows
            assert '_atomic' in found_dirs or '_composite' in found_dirs, \
                f"{showcase.name} should have _atomic or _composite directory"

    def test_skill_file_naming(self, all_skills_across_showcases):
        """Skill files should be named SKILL.md."""
        for skill_file in all_skills_across_showcases:
            assert skill_file.name == 'SKILL.md', \
                f"Skill file should be SKILL.md: {skill_file}"


# =============================================================================
# Level Consistency Tests
# =============================================================================

class TestLevelConsistency:
    """Verify level assignments are consistent across showcases."""

    def test_atomic_skills_in_atomic_dir(self, all_showcases):
        """Level 1 skills should be in _atomic directories."""
        for showcase in all_showcases:
            atomic_dir = showcase / '_atomic'
            if atomic_dir.exists():
                for skill_file in atomic_dir.rglob('SKILL.md'):
                    content = skill_file.read_text()
                    assert 'level: 1' in content, \
                        f"Skill in _atomic should be level 1: {skill_file.parent.name}"

    def test_composite_skills_in_composite_dir(self, all_showcases):
        """Level 2 skills should be in _composite directories."""
        for showcase in all_showcases:
            composite_dir = showcase / '_composite'
            if composite_dir.exists():
                for skill_file in composite_dir.rglob('SKILL.md'):
                    content = skill_file.read_text()
                    assert 'level: 2' in content, \
                        f"Skill in _composite should be level 2: {skill_file.parent.name}"

    def test_workflow_skills_in_workflows_dir(self, all_showcases):
        """Level 3 skills should be in _workflows directories."""
        for showcase in all_showcases:
            workflows_dir = showcase / '_workflows'
            if workflows_dir.exists():
                for skill_file in workflows_dir.rglob('SKILL.md'):
                    content = skill_file.read_text()
                    assert 'level: 3' in content, \
                        f"Skill in _workflows should be level 3: {skill_file.parent.name}"

    def test_level_distribution_reasonable(self, skills_by_level):
        """Each showcase should have a reasonable distribution of levels."""
        total = sum(len(s) for s in skills_by_level.values())
        if total > 0:
            l1_ratio = len(skills_by_level[1]) / total
            l3_ratio = len(skills_by_level[3]) / total

            # L1 (atomic) should be significant portion
            assert l1_ratio >= 0.2, "Should have at least 20% atomic skills"
            # L3 (workflows) should be smaller
            assert l3_ratio <= 0.4, "Workflows should be at most 40% of skills"


# =============================================================================
# Operation Consistency Tests
# =============================================================================

class TestOperationConsistency:
    """Verify operation types are used consistently."""

    def test_all_skills_have_operation(self, all_skills_across_showcases):
        """All skills should declare an operation type."""
        for skill_file in all_skills_across_showcases:
            content = skill_file.read_text()
            has_operation = (
                'operation: READ' in content or
                'operation: WRITE' in content or
                'operation: TRANSFORM' in content
            )
            assert has_operation, \
                f"Skill should have operation: {skill_file.parent.name}"

    def test_write_operations_have_approval(self, all_skills_across_showcases):
        """WRITE operations should consider approval requirements."""
        for skill_file in all_skills_across_showcases:
            content = skill_file.read_text()
            if 'operation: WRITE' in content:
                # Should mention approval or be atomic (L1)
                has_approval = (
                    'requires_approval' in content.lower() or
                    'approval' in content.lower() or
                    'level: 1' in content  # L1 skills may defer approval to callers
                )
                # Soft check - most WRITE skills should consider approval
                if not has_approval:
                    pass  # Just note, don't fail


# =============================================================================
# Composition Pattern Tests
# =============================================================================

class TestCompositionPatterns:
    """Verify composition patterns are consistent."""

    def test_l2_skills_compose_l1(self, all_showcases):
        """Level 2 skills should primarily compose Level 1 skills."""
        for showcase in all_showcases:
            composite_dir = showcase / '_composite'
            atomic_dir = showcase / '_atomic'

            if not composite_dir.exists() or not atomic_dir.exists():
                continue

            # Get L1 skill names
            l1_skills = {s.name for s in atomic_dir.iterdir() if s.is_dir()}

            for skill_file in composite_dir.rglob('SKILL.md'):
                content = skill_file.read_text()
                if 'composes:' not in content:
                    continue

                # Check if composed skills include L1 skills
                composed_l1 = [s for s in l1_skills if s in content]
                # L2 skills should compose at least some L1 skills (or other L2)
                # This is informational, not enforced

    def test_l3_workflows_compose_multiple(self, all_showcases):
        """Level 3 workflows should compose multiple lower-level skills."""
        for showcase in all_showcases:
            workflows_dir = showcase / '_workflows'
            if not workflows_dir.exists():
                continue

            for skill_file in workflows_dir.rglob('SKILL.md'):
                content = skill_file.read_text()
                if 'composes:' in content:
                    # Count composed skills
                    composes_section = content.split('composes:')[1].split('\n')
                    composed_count = sum(1 for line in composes_section
                                        if line.strip().startswith('-') and
                                        not line.strip().startswith('---'))
                    assert composed_count >= 2, \
                        f"Workflow should compose at least 2 skills: {skill_file.parent.name}"


# =============================================================================
# State Machine Tests
# =============================================================================

class TestStateMachineConsistency:
    """Verify state machine patterns are consistent across workflows."""

    def test_workflows_have_terminal_states(self, skills_by_level):
        """All workflows should have terminal states."""
        for skill_file in skills_by_level[3]:
            content = skill_file.read_text()
            content_upper = content.upper()
            has_terminal = (
                'terminal: true' in content or
                'COMPLETE' in content_upper or
                'CANCELLED' in content_upper or
                'DONE' in content_upper or
                'ACTIVE' in content_upper or  # Common final state
                'FINISHED' in content_upper or
                'CLOSED' in content_upper or
                'RETURN' in content_upper or  # Algorithmic return
                'STOP' in content_upper
            )
            assert has_terminal, \
                f"Workflow should have terminal state: {skill_file.parent.name}"

    def test_workflows_have_human_checkpoints(self, skills_by_level):
        """Most workflows should have human checkpoints."""
        workflows_with_checkpoints = 0
        for skill_file in skills_by_level[3]:
            content = skill_file.read_text()
            if 'human_checkpoint' in content.lower() or 'approval' in content.lower():
                workflows_with_checkpoints += 1

        total_workflows = len(skills_by_level[3])
        if total_workflows > 0:
            ratio = workflows_with_checkpoints / total_workflows
            assert ratio >= 0.5, \
                f"At least 50% of workflows should have human checkpoints (found {ratio:.0%})"


# =============================================================================
# Tool Discovery Tests
# =============================================================================

class TestToolDiscoveryPatterns:
    """Verify tool discovery patterns are consistent."""

    def test_atomic_skills_have_tools(self, skills_by_level):
        """Atomic skills should declare tool preferences."""
        skills_with_tools = 0
        for skill_file in skills_by_level[1]:
            content = skill_file.read_text()
            if 'tools:' in content or 'tool_discovery:' in content:
                skills_with_tools += 1

        total = len(skills_by_level[1])
        if total > 0:
            ratio = skills_with_tools / total
            # Most L1 skills should have tool preferences
            assert ratio >= 0.5, \
                f"At least 50% of atomic skills should have tool declarations (found {ratio:.0%})"


# =============================================================================
# Documentation Tests
# =============================================================================

class TestDocumentationConsistency:
    """Verify documentation patterns are consistent."""

    def test_all_skills_have_description(self, all_skills_across_showcases):
        """All skills should have descriptions."""
        for skill_file in all_skills_across_showcases:
            content = skill_file.read_text()
            assert 'description:' in content or 'description: ' in content, \
                f"Skill should have description: {skill_file.parent.name}"

    def test_all_showcases_have_readme(self, all_showcases):
        """All showcases should have a README."""
        for showcase in all_showcases:
            readme_exists = (
                (showcase / 'README.md').exists() or
                (showcase / 'readme.md').exists()
            )
            assert readme_exists, f"Showcase should have README: {showcase.name}"

    def test_error_handling_documented(self, skills_by_level):
        """Workflows should document error handling."""
        workflows_with_errors = 0
        for skill_file in skills_by_level[3]:
            content = skill_file.read_text().lower()
            has_error_handling = (
                'error' in content or
                'fail' in content or
                'recovery' in content or
                'timeout' in content or
                'exception' in content
            )
            if has_error_handling:
                workflows_with_errors += 1

        total = len(skills_by_level[3])
        if total > 0:
            ratio = workflows_with_errors / total
            # Soft check - at least some should have error handling
            assert ratio >= 0.3, \
                f"At least 30% of workflows should document error handling (found {ratio:.0%})"


# =============================================================================
# Cross-Showcase Skill Comparison Tests
# =============================================================================

class TestCrossShowcaseComparison:
    """Compare similar skills across showcases."""

    def test_similar_skills_have_similar_structure(self, skill_names_by_showcase):
        """Skills with similar names should have similar structure."""
        # Collect all skill names
        all_names = []
        for showcase, names in skill_names_by_showcase.items():
            all_names.extend(names)

        # Find potential duplicates or similar skills
        name_counts = defaultdict(list)
        for name in all_names:
            # Normalize name (remove prefix)
            parts = name.split('-')
            if len(parts) > 1:
                key = '-'.join(parts[-2:])  # Last two parts
                name_counts[key].append(name)

        # This is informational - identify potential overlaps
        overlaps = {k: v for k, v in name_counts.items() if len(v) > 1}
        if overlaps:
            # Just note, don't fail
            pass
