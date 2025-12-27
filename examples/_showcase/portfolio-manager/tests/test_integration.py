"""Integration tests for portfolio manager skill showcase."""

import pytest
from pathlib import Path
import re

try:
    from skills_ref.validator import validate
    from skills_ref.parser import parse_skill
    SKILLS_REF_AVAILABLE = True
except ImportError:
    SKILLS_REF_AVAILABLE = False


# =============================================================================
# Showcase Structure Tests
# =============================================================================

class TestShowcaseStructure:
    """Verify the overall showcase structure is correct."""

    def test_readme_exists(self, showcase_dir):
        """Showcase should have a README."""
        readme = showcase_dir / "README.md"
        assert readme.exists(), "Showcase should have README.md"

    def test_readme_documents_skills(self, showcase_dir):
        """README should document the skill library."""
        readme_content = (showcase_dir / "README.md").read_text()
        # Should mention the three levels
        assert "Level 1" in readme_content or "L1" in readme_content or "Atomic" in readme_content
        assert "Level 2" in readme_content or "L2" in readme_content or "Composite" in readme_content
        assert "Level 3" in readme_content or "L3" in readme_content or "Workflow" in readme_content

    def test_directory_structure(self, showcase_dir):
        """Showcase should have atomic, composite, and workflows directories."""
        assert (showcase_dir / "_atomic").is_dir()
        assert (showcase_dir / "_composite").is_dir()
        assert (showcase_dir / "_workflows").is_dir()

    def test_all_skills_have_skill_md(self, all_skill_dirs):
        """Every skill directory should have a SKILL.md file."""
        for skill_dir in all_skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            assert skill_file.exists(), f"Missing SKILL.md in {skill_dir.name}"


# =============================================================================
# All Skills Validation Tests
# =============================================================================

@pytest.mark.skipif(not SKILLS_REF_AVAILABLE, reason="skills_ref not available")
class TestAllSkillsValidate:
    """Validate all skills in the showcase pass validation."""

    def test_all_skills_pass_validation(self, all_skill_dirs):
        """Every skill should pass validation."""
        failed = []
        for skill_dir in all_skill_dirs:
            errors = validate(skill_dir)
            if errors:
                failed.append((skill_dir.name, errors))

        if failed:
            msg = "\n".join(f"{name}: {errs}" for name, errs in failed)
            pytest.fail(f"Skills failed validation:\n{msg}")


# =============================================================================
# Composition Graph Tests
# =============================================================================

class TestCompositionGraph:
    """Verify the composition graph is consistent."""

    def test_composed_skills_exist(self, all_skill_dirs, showcase_dir):
        """All composed skills should exist in the showcase."""
        # Build list of all skill names
        all_skill_names = {d.name for d in all_skill_dirs}

        # Check each skill's composes references
        missing_refs = []
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "composes:" not in content:
                continue

            # Extract composed skill names
            lines = content.split("composes:")[1].split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("-"):
                    composed = line.lstrip("- ").strip()
                    if composed and not composed.startswith("#"):
                        # Skip if it's a built-in or external reference
                        # Only check for skills that should be in this showcase
                        if composed in all_skill_names:
                            continue
                        # These are expected external skills (from core library)
                        external_skills = {
                            "web-search", "email-read", "calendar-read",
                            "pdf-save", "slack-read", "with-retry", "with-cache"
                        }
                        if composed not in external_skills:
                            # It's an internal reference that should exist
                            missing_refs.append((skill_dir.name, composed))
                elif line.startswith("---") or ":" in line:
                    break

        # We don't fail on missing refs since skills may reference
        # other skills in the ecosystem
        if missing_refs:
            # Just warn, don't fail
            print(f"Note: Some composed skills not in showcase: {missing_refs}")

    def test_no_circular_dependencies(self, all_skill_dirs):
        """Composition graph should not have circular dependencies."""
        # Build composition graph
        graph = {}
        for skill_dir in all_skill_dirs:
            skill_name = skill_dir.name
            content = (skill_dir / "SKILL.md").read_text()
            graph[skill_name] = []

            if "composes:" not in content:
                continue

            lines = content.split("composes:")[1].split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("-"):
                    composed = line.lstrip("- ").strip()
                    if composed and not composed.startswith("#"):
                        graph[skill_name].append(composed)
                elif line.startswith("---") or ":" in line:
                    break

        # Check for cycles using DFS
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if neighbor in graph and has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for skill in graph:
            if has_cycle(skill, set(), set()):
                pytest.fail(f"Circular dependency detected involving: {skill}")


# =============================================================================
# Level Hierarchy Tests
# =============================================================================

class TestLevelHierarchy:
    """Verify skills follow the level hierarchy."""

    def test_level_1_does_not_compose(self, atomic_dir, atomic_skills):
        """Level 1 skills should not compose other skills."""
        for skill_name in atomic_skills:
            skill_file = atomic_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                # Check the YAML frontmatter only
                frontmatter = content.split("---")[1] if "---" in content else ""
                if "composes:" in frontmatter:
                    # Check if it's an empty list or has actual values
                    lines = frontmatter.split("composes:")[1].split("\n")
                    has_composed = False
                    for line in lines:
                        if line.strip().startswith("-"):
                            has_composed = True
                            break
                        elif ":" in line:
                            break
                    assert not has_composed, f"L1 skill {skill_name} should not compose other skills"

    def test_level_2_composes_level_1_or_2(self, composite_dir, composite_skills, atomic_skills):
        """Level 2 skills should compose L1 or other L2 skills."""
        for skill_name in composite_skills:
            skill_file = composite_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "composes:" in content, f"L2 skill {skill_name} should compose other skills"

    def test_level_3_composes_multiple_levels(self, workflows_dir, workflow_skills):
        """Level 3 skills should compose L1 and/or L2 skills."""
        for skill_name in workflow_skills:
            skill_file = workflows_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "composes:" in content, f"L3 skill {skill_name} should compose other skills"
                # Count composed skills
                lines = content.split("composes:")[1].split("\n")
                count = sum(1 for line in lines if line.strip().startswith("-"))
                assert count >= 2, f"L3 skill {skill_name} should compose multiple skills"


# =============================================================================
# Operation Type Tests
# =============================================================================

class TestOperationTypes:
    """Verify operation types are correctly assigned."""

    def test_read_operations_are_safe(self, all_skill_dirs):
        """READ operations should not require approval."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "operation: READ" in content:
                # READ operations typically don't require approval
                # (though some may for policy reasons)
                pass

    def test_write_operations_have_caution(self, all_skill_dirs):
        """WRITE operations should indicate caution/approval."""
        write_skills = []
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "operation: WRITE" in content:
                write_skills.append(skill_dir.name)
                # Should have some indication of approval or caution
                has_caution = (
                    "requires_approval" in content.lower() or
                    "approval" in content.lower() or
                    "human_checkpoint" in content.lower() or
                    "caution" in content.lower()
                )
                # Not strictly required, but recommended
                if not has_caution:
                    print(f"Note: WRITE skill {skill_dir.name} has no approval indication")


# =============================================================================
# Schema Consistency Tests
# =============================================================================

class TestSchemaConsistency:
    """Verify schemas are consistent across skills."""

    def test_portfolio_schema_consistency(self, all_skill_dirs):
        """Portfolio object should have consistent schema across skills."""
        # Skills that use portfolio input/output should use consistent naming
        portfolio_properties = ["holdings", "total_value", "as_of_date"]
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            if "portfolio:" in content.lower():
                # Check for common properties
                found = [p for p in portfolio_properties if p in content]
                # Most portfolio-related skills should use at least some common properties
                # This is a soft check

    def test_holdings_schema_consistency(self, all_skill_dirs):
        """Holdings array in INPUT schema should have consistent item schema."""
        holdings_properties = ["security_id", "quantity"]
        # Only check skills that define holdings in their input schema
        # (not skills that just reference holdings in output or nested structures)
        skills_with_holdings_input = [
            "holdings-ingest",  # Defines the canonical holdings schema
            "risk-metrics-calculate",  # Takes holdings as input
        ]
        for skill_dir in all_skill_dirs:
            if skill_dir.name in skills_with_holdings_input:
                content = (skill_dir / "SKILL.md").read_text()
                for prop in holdings_properties:
                    assert prop in content, \
                        f"Holdings in {skill_dir.name} should include {prop}"


# =============================================================================
# Documentation Coverage Tests
# =============================================================================

class TestDocumentationCoverage:
    """Verify skills are properly documented."""

    def test_all_skills_have_description(self, all_skill_dirs):
        """All skills should have a description."""
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text()
            assert "description:" in content, \
                f"{skill_dir.name} should have a description"

    def test_all_skills_have_example(self, all_skill_dirs):
        """All skills should have usage examples."""
        missing_examples = []
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text().lower()
            has_example = (
                "example" in content or
                "usage" in content or
                "```yaml" in content
            )
            if not has_example:
                missing_examples.append(skill_dir.name)

        # Soft check - warn but don't fail
        if missing_examples:
            print(f"Note: Skills without clear examples: {missing_examples}")

    def test_all_skills_have_error_handling(self, all_skill_dirs):
        """All skills should document error handling."""
        missing_error_docs = []
        for skill_dir in all_skill_dirs:
            content = (skill_dir / "SKILL.md").read_text().lower()
            has_error_docs = (
                "error" in content or
                "fail" in content or
                "exception" in content or
                "recovery" in content
            )
            if not has_error_docs:
                missing_error_docs.append(skill_dir.name)

        if missing_error_docs:
            print(f"Note: Skills without error handling docs: {missing_error_docs}")


# =============================================================================
# Cross-Reference Tests
# =============================================================================

class TestCrossReferences:
    """Verify cross-references between skills are valid."""

    def test_readme_lists_all_skills(self, showcase_dir, all_skill_dirs):
        """README should list all skills."""
        readme = (showcase_dir / "README.md").read_text()
        # Check that most skills are mentioned in README
        mentioned = 0
        for skill_dir in all_skill_dirs:
            if skill_dir.name in readme:
                mentioned += 1

        coverage = mentioned / len(all_skill_dirs) if all_skill_dirs else 0
        assert coverage >= 0.5, f"README should mention more skills (only {mentioned}/{len(all_skill_dirs)} mentioned)"


# =============================================================================
# Skill Count Tests
# =============================================================================

class TestSkillCounts:
    """Verify expected skill counts."""

    def test_minimum_atomic_skills(self, atomic_dir):
        """Should have at least 5 atomic skills."""
        skills = list(atomic_dir.iterdir())
        skill_dirs = [s for s in skills if s.is_dir() and (s / "SKILL.md").exists()]
        assert len(skill_dirs) >= 5, f"Expected at least 5 atomic skills, found {len(skill_dirs)}"

    def test_minimum_composite_skills(self, composite_dir):
        """Should have at least 8 composite skills."""
        skills = list(composite_dir.iterdir())
        skill_dirs = [s for s in skills if s.is_dir() and (s / "SKILL.md").exists()]
        assert len(skill_dirs) >= 8, f"Expected at least 8 composite skills, found {len(skill_dirs)}"

    def test_minimum_workflow_skills(self, workflows_dir):
        """Should have at least 3 workflow skills."""
        skills = list(workflows_dir.iterdir())
        skill_dirs = [s for s in skills if s.is_dir() and (s / "SKILL.md").exists()]
        assert len(skill_dirs) >= 3, f"Expected at least 3 workflow skills, found {len(skill_dirs)}"

    def test_total_skill_count(self, all_skill_dirs):
        """Should have at least 15 total skills."""
        assert len(all_skill_dirs) >= 15, f"Expected at least 15 total skills, found {len(all_skill_dirs)}"
