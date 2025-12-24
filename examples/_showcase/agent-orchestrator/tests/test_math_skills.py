"""
Tests for strict math calculation skills.

These skills ensure LLMs use Python execution instead of mental math,
providing auditability and accuracy for all calculations.
"""

import pytest
from pathlib import Path
import yaml
import re

# Test configuration
SHOWCASE_ROOT = Path(__file__).parent.parent
ATOMIC_DIR = SHOWCASE_ROOT / "_atomic"
COMPOSITE_DIR = SHOWCASE_ROOT / "_composite"

MATH_ATOMIC_SKILLS = ["math-execute"]
MATH_COMPOSITE_SKILLS = ["math-solve"]
ALL_MATH_SKILLS = MATH_ATOMIC_SKILLS + MATH_COMPOSITE_SKILLS


def read_skill(skill_name: str) -> str:
    """Read a skill file and return its content."""
    # Check atomic first
    atomic_path = ATOMIC_DIR / skill_name / "SKILL.md"
    if atomic_path.exists():
        return atomic_path.read_text()

    # Check composite
    composite_path = COMPOSITE_DIR / skill_name / "SKILL.md"
    if composite_path.exists():
        return composite_path.read_text()

    pytest.fail(f"Skill {skill_name} not found")


def extract_yaml_block(content: str, block_name: str) -> dict:
    """Extract a YAML code block by name."""
    pattern = rf"```yaml\n({block_name}:.*?)```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}


def extract_metadata(content: str) -> dict:
    """Extract metadata YAML block."""
    pattern = r"## Metadata\s*```yaml\n(.*?)```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}


class TestMathSkillsExist:
    """Verify all math skills exist."""

    @pytest.mark.parametrize("skill_name", MATH_ATOMIC_SKILLS)
    def test_atomic_skill_exists(self, skill_name):
        """Each atomic math skill should have a SKILL.md file."""
        skill_path = ATOMIC_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing atomic skill: {skill_name}"

    @pytest.mark.parametrize("skill_name", MATH_COMPOSITE_SKILLS)
    def test_composite_skill_exists(self, skill_name):
        """Each composite math skill should have a SKILL.md file."""
        skill_path = COMPOSITE_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing composite skill: {skill_name}"


class TestMathExecuteSkill:
    """Tests for the math-execute atomic skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("math-execute")

    def test_has_critical_rules_section(self, skill_content):
        """Must have critical rules about never using mental math."""
        assert "## CRITICAL RULES" in skill_content
        assert "NEVER perform mental math" in skill_content

    def test_has_execute_operation(self, skill_content):
        """math-execute should be an EXECUTE operation."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("operation") == "EXECUTE"

    def test_has_math_domain(self, skill_content):
        """Should be in math domain."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("domain") == "math"

    def test_is_level_1(self, skill_content):
        """Should be level 1 (atomic)."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("level") == 1

    def test_requires_code_input(self, skill_content):
        """Must require 'code' as input."""
        assert "required:" in skill_content
        assert "- code" in skill_content

    def test_has_safe_mode_option(self, skill_content):
        """Should have safe_mode option to restrict dangerous operations."""
        assert "safe_mode:" in skill_content
        assert "restricts to math-safe operations" in skill_content.lower() or \
               "Disables file I/O" in skill_content

    def test_output_includes_code_executed(self, skill_content):
        """Output must include code_executed for audit trail."""
        assert "code_executed:" in skill_content
        assert "audit" in skill_content.lower()

    def test_output_includes_success(self, skill_content):
        """Output must include success boolean."""
        assert "success:" in skill_content

    def test_output_includes_result(self, skill_content):
        """Output must include result."""
        assert "result:" in skill_content

    def test_has_execution_time(self, skill_content):
        """Should track execution time."""
        assert "execution_time_ms" in skill_content

    def test_has_precision_option(self, skill_content):
        """Should have precision option for floating point."""
        assert "precision:" in skill_content

    def test_has_timeout_option(self, skill_content):
        """Should have timeout for runaway calculations."""
        assert "timeout" in skill_content.lower()

    def test_has_error_handling(self, skill_content):
        """Must handle errors properly."""
        assert "error:" in skill_content
        assert "ZeroDivisionError" in skill_content or "ZERO_DIVISION" in skill_content

    def test_has_security_validation(self, skill_content):
        """Should validate code for security in safe mode."""
        assert "FORBIDDEN" in skill_content or "forbidden" in skill_content
        assert "exec" in skill_content or "eval" in skill_content

    def test_has_allowed_modules_list(self, skill_content):
        """Should define allowed modules for safe execution."""
        assert "math" in skill_content
        assert "statistics" in skill_content
        assert "decimal" in skill_content

    def test_has_examples(self, skill_content):
        """Should include usage examples."""
        assert "## Examples" in skill_content
        assert "25 * 47" in skill_content or "25 × 47" in skill_content


class TestMathSolveSkill:
    """Tests for the math-solve composite skill."""

    @pytest.fixture
    def skill_content(self) -> str:
        return read_skill("math-solve")

    def test_has_critical_rules_section(self, skill_content):
        """Must have critical rules about always using this skill."""
        assert "## CRITICAL RULES" in skill_content
        assert "MUST be invoked" in skill_content or "MUST use" in skill_content

    def test_composes_math_execute(self, skill_content):
        """Must compose math-execute skill."""
        assert "math-execute" in skill_content
        assert "## Composes" in skill_content

    def test_has_transform_operation(self, skill_content):
        """math-solve should be a TRANSFORM operation."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("operation") == "TRANSFORM"

    def test_has_math_domain(self, skill_content):
        """Should be in math domain."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("domain") == "math"

    def test_is_level_2(self, skill_content):
        """Should be level 2 (composite)."""
        metadata = extract_metadata(skill_content)
        assert metadata.get("level") == 2

    def test_requires_problem_input(self, skill_content):
        """Must require 'problem' as input (natural language)."""
        assert "required:" in skill_content
        assert "- problem" in skill_content

    def test_output_includes_python_code(self, skill_content):
        """Output must include generated Python code for audit."""
        assert "python_code:" in skill_content

    def test_output_includes_answer(self, skill_content):
        """Output must include human-readable answer."""
        assert "answer:" in skill_content

    def test_output_includes_execution_result(self, skill_content):
        """Output must include full execution result from math-execute."""
        assert "execution_result:" in skill_content

    def test_has_problem_analysis(self, skill_content):
        """Should analyze and categorize the problem."""
        assert "problem_analysis:" in skill_content or "problem_type:" in skill_content

    def test_has_show_steps_option(self, skill_content):
        """Should have option to show step-by-step breakdown."""
        assert "show_steps:" in skill_content or "steps:" in skill_content

    def test_has_verify_option(self, skill_content):
        """Should have option to verify/validate results."""
        assert "verify:" in skill_content or "validation:" in skill_content

    def test_handles_arithmetic(self, skill_content):
        """Should handle arithmetic problems."""
        assert "arithmetic" in skill_content.lower()

    def test_handles_percentages(self, skill_content):
        """Should handle percentage calculations."""
        assert "percentage" in skill_content.lower()
        assert "tip" in skill_content.lower() or "%" in skill_content

    def test_handles_financial(self, skill_content):
        """Should handle financial calculations."""
        assert "financial" in skill_content.lower()
        assert "interest" in skill_content.lower() or "compound" in skill_content.lower()

    def test_handles_statistical(self, skill_content):
        """Should handle statistical calculations."""
        assert "statistical" in skill_content.lower()
        assert "mean" in skill_content.lower() or "average" in skill_content.lower()

    def test_has_detection_triggers(self, skill_content):
        """Should list triggers that indicate math is needed."""
        assert "calculate" in skill_content.lower()
        assert "what is" in skill_content.lower() or "triggers:" in skill_content

    def test_has_multiple_examples(self, skill_content):
        """Should have multiple examples covering different problem types."""
        assert "## Examples" in skill_content
        examples_section = skill_content.split("## Examples")[1]
        # Should have at least 3 different examples
        example_count = examples_section.count("### ")
        assert example_count >= 3, f"Expected at least 3 examples, found {example_count}"

    def test_has_validation_rules(self, skill_content):
        """Should have validation rules for result checking."""
        assert "validation" in skill_content.lower()
        assert "check" in skill_content.lower()

    def test_has_error_handling(self, skill_content):
        """Should document error handling."""
        assert "## Error" in skill_content or "Error Handling" in skill_content

    def test_includes_audit_trail_emphasis(self, skill_content):
        """Should emphasize auditability."""
        assert "audit" in skill_content.lower()
        # The python_code should be described as audit trail
        assert "THIS IS THE AUDIT TRAIL" in skill_content or \
               "audit trail" in skill_content.lower()


class TestMathSkillsIntegration:
    """Integration tests for math skills working together."""

    def test_math_solve_references_math_execute(self):
        """math-solve should reference math-execute in composition."""
        solve_content = read_skill("math-solve")
        assert "math-execute" in solve_content

    def test_both_skills_have_audit_emphasis(self):
        """Both skills should emphasize auditability."""
        execute_content = read_skill("math-execute")
        solve_content = read_skill("math-solve")

        assert "audit" in execute_content.lower()
        assert "audit" in solve_content.lower()

    def test_both_skills_reject_mental_math(self):
        """Both skills should explicitly reject mental math."""
        execute_content = read_skill("math-execute")
        solve_content = read_skill("math-solve")

        # At least one should have explicit mental math warning
        combined = execute_content + solve_content
        assert "mental math" in combined.lower() or \
               "NEVER perform" in combined or \
               "NEVER attempt" in combined

    def test_consistent_domain(self):
        """All math skills should have same domain."""
        execute_meta = extract_metadata(read_skill("math-execute"))
        solve_meta = extract_metadata(read_skill("math-solve"))

        assert execute_meta.get("domain") == solve_meta.get("domain") == "math"

    def test_level_hierarchy(self):
        """Composite should be higher level than atomic."""
        execute_meta = extract_metadata(read_skill("math-execute"))
        solve_meta = extract_metadata(read_skill("math-solve"))

        assert execute_meta.get("level") == 1
        assert solve_meta.get("level") == 2
        assert solve_meta.get("level") > execute_meta.get("level")


class TestMathSkillsAuditability:
    """Tests specifically for auditability features."""

    def test_execute_returns_exact_code(self):
        """math-execute must return the exact code that was run."""
        content = read_skill("math-execute")
        # Check output schema has code_executed
        assert "code_executed:" in content
        assert "Exact Python code" in content or "exact code" in content.lower()

    def test_solve_includes_generated_code(self):
        """math-solve must include the Python code it generated."""
        content = read_skill("math-solve")
        assert "python_code:" in content
        # Should explain this is for verification
        assert "verify" in content.lower() or "audit" in content.lower()

    def test_examples_show_code_in_output(self):
        """Examples should demonstrate code being returned."""
        solve_content = read_skill("math-solve")
        execute_content = read_skill("math-execute")

        # Both should have examples with code in output
        assert "code_executed:" in execute_content.split("## Examples")[1]
        assert "python_code:" in solve_content.split("## Examples")[1]


class TestMathSkillsSafety:
    """Tests for safety features."""

    def test_execute_has_safe_mode(self):
        """math-execute should have safe_mode to prevent dangerous code."""
        content = read_skill("math-execute")
        assert "safe_mode:" in content

    def test_execute_blocks_dangerous_functions(self):
        """Should block dangerous functions in safe mode."""
        content = read_skill("math-execute")
        dangerous = ["exec", "eval", "open", "__import__"]
        blocked_count = sum(1 for d in dangerous if d in content)
        assert blocked_count >= 2, "Should mention blocking dangerous functions"

    def test_execute_has_timeout(self):
        """Should have timeout to prevent infinite loops."""
        content = read_skill("math-execute")
        assert "timeout" in content.lower()

    def test_execute_whitelist_modules(self):
        """Should whitelist safe math modules."""
        content = read_skill("math-execute")
        safe_modules = ["math", "statistics", "decimal"]
        present_count = sum(1 for m in safe_modules if m in content)
        assert present_count >= 2, "Should list safe modules"


class TestMathSkillsCompleteness:
    """Tests for completeness of documentation."""

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_description(self, skill_name):
        """Each skill should have a description."""
        content = read_skill(skill_name)
        assert "## Description" in content

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_metadata(self, skill_name):
        """Each skill should have metadata."""
        content = read_skill(skill_name)
        assert "## Metadata" in content

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_input_schema(self, skill_name):
        """Each skill should have input schema."""
        content = read_skill(skill_name)
        assert "## Input Schema" in content or "inputSchema:" in content

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_output_schema(self, skill_name):
        """Each skill should have output schema."""
        content = read_skill(skill_name)
        assert "## Output Schema" in content or "outputSchema:" in content

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_examples(self, skill_name):
        """Each skill should have examples."""
        content = read_skill(skill_name)
        assert "## Examples" in content

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_error_section(self, skill_name):
        """Each skill should document errors."""
        content = read_skill(skill_name)
        assert "Error" in content  # Error Codes or Error Handling


class TestMathSkillsTags:
    """Tests for proper tagging."""

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_math_tag(self, skill_name):
        """All math skills should have 'math' tag."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        tags = metadata.get("tags", [])
        assert "math" in tags, f"{skill_name} should have 'math' tag"

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_audit_or_strict_tag(self, skill_name):
        """Math skills should have 'audit' or 'strict' tag."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        tags = metadata.get("tags", [])
        assert "audit" in tags or "strict" in tags, \
            f"{skill_name} should have 'audit' or 'strict' tag"

    @pytest.mark.parametrize("skill_name", ALL_MATH_SKILLS)
    def test_has_python_tag(self, skill_name):
        """Math skills should have 'python' tag (execution method)."""
        content = read_skill(skill_name)
        metadata = extract_metadata(content)
        tags = metadata.get("tags", [])
        assert "python" in tags, f"{skill_name} should have 'python' tag"
