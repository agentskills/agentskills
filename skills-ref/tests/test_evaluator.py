"""Tests for the skill quality evaluation framework."""

import tempfile
from pathlib import Path

import pytest

from skills_ref.evaluator import (
    EvaluationFinding,
    EvaluationResult,
    Severity,
    SkillEvaluator,
    evaluate_skill,
)


@pytest.fixture
def temp_skill_dir():
    """Create a temporary skill directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def minimal_valid_skill(temp_skill_dir):
    """Create a minimal valid skill for testing."""
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: A test skill demonstrating when to use skill evaluation features
---

## Overview

This is a test skill with adequate content for evaluation.

## When to Use

Use this skill when testing the evaluation framework.

## Usage

Simply call the evaluate function on this skill directory.

## Examples

```python
from skills_ref import evaluate_skill

result = evaluate_skill(Path("test-skill"))
print(result.overall_score)
```
""",
        encoding="utf-8",
    )
    return temp_skill_dir


@pytest.fixture
def incomplete_skill(temp_skill_dir):
    """Create an incomplete skill for testing."""
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: incomplete-skill
description: Too short
---

Brief content.
""",
        encoding="utf-8",
    )
    return temp_skill_dir


def test_evaluator_initialization():
    """Test that evaluator can be initialized."""
    evaluator = SkillEvaluator()
    assert evaluator.min_description_length == 20
    assert evaluator.max_description_length == 500
    assert len(evaluator.recommended_sections) > 0


def test_evaluate_minimal_valid_skill(minimal_valid_skill):
    """Test evaluation of a minimal valid skill."""
    result = evaluate_skill(minimal_valid_skill)

    assert isinstance(result, EvaluationResult)
    assert result.skill_name == "test-skill"
    assert result.skill_path == minimal_valid_skill
    assert not result.has_errors
    assert result.overall_score > 0


def test_evaluate_incomplete_skill(incomplete_skill):
    """Test evaluation of an incomplete skill."""
    result = evaluate_skill(incomplete_skill)

    assert result.skill_name == "incomplete-skill"
    assert result.has_warnings
    assert result.overall_score < 100

    # Should have warnings about short description and content
    categories = [f.category for f in result.findings]
    assert "clarity" in categories or "completeness" in categories


def test_missing_skill_md(temp_skill_dir):
    """Test evaluation when SKILL.md is missing."""
    result = evaluate_skill(temp_skill_dir)

    assert result.has_errors
    error_messages = [f.message for f in result.findings if f.severity == Severity.ERROR]
    assert any("SKILL.md file not found" in msg for msg in error_messages)


def test_evaluation_finding_creation():
    """Test creating evaluation findings."""
    finding = EvaluationFinding(
        severity=Severity.WARNING,
        category="clarity",
        message="Test message",
        suggestion="Test suggestion",
    )

    assert finding.severity == Severity.WARNING
    assert finding.category == "clarity"
    assert finding.message == "Test message"
    assert finding.suggestion == "Test suggestion"


def test_evaluation_result_properties(minimal_valid_skill):
    """Test EvaluationResult properties."""
    result = evaluate_skill(minimal_valid_skill)

    # Test overall_score calculation
    assert 0 <= result.overall_score <= 100
    if result.scores:
        expected_avg = sum(result.scores.values()) / len(result.scores)
        assert result.overall_score == expected_avg


def test_description_length_validation(temp_skill_dir):
    """Test description length validation."""
    # Too short
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test
description: Short
---

Some content here that is long enough.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    assert any(
        "too short" in f.message.lower()
        for f in result.findings
        if f.category == "clarity"
    )

    # Too long
    long_desc = "A" * 600
    skill_md.write_text(
        f"""---
name: test
description: {long_desc}
---

Some content.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    assert any(
        "too long" in f.message.lower()
        for f in result.findings
        if f.category == "clarity"
    )


def test_missing_sections_detection(temp_skill_dir):
    """Test detection of missing recommended sections."""
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: A skill for testing section detection when evaluating
---

Just some basic content without the recommended sections.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    assert any(
        "missing recommended sections" in f.message.lower()
        for f in result.findings
        if f.category == "structure"
    )


def test_examples_detection(temp_skill_dir):
    """Test detection of code examples."""
    # Skill without examples
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: A skill for testing example detection when evaluating
---

Content without any examples.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    assert any(
        "example" in f.message.lower()
        for f in result.findings
        if f.category == "completeness"
    )

    # Skill with code example
    skill_md.write_text(
        """---
name: test-skill
description: A skill for testing example detection when evaluating
---

Here's an example:

```python
print("example")
```
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    example_findings = [
        f
        for f in result.findings
        if "example" in f.message.lower() and f.category == "completeness"
    ]
    assert len(example_findings) == 0


def test_score_calculation_with_errors():
    """Test score calculation with various finding severities."""
    result = EvaluationResult(skill_path=Path("."), skill_name="test")

    # Add findings with different severities
    result.findings = [
        EvaluationFinding(
            severity=Severity.ERROR, category="completeness", message="Error 1"
        ),
        EvaluationFinding(
            severity=Severity.WARNING, category="clarity", message="Warning 1"
        ),
        EvaluationFinding(
            severity=Severity.INFO, category="structure", message="Info 1"
        ),
    ]

    evaluator = SkillEvaluator()
    evaluator._calculate_scores(result)

    # Errors should deduct 30 points
    assert result.scores["completeness"] == 70
    # Warnings should deduct 15 points
    assert result.scores["clarity"] == 85
    # Info should deduct 5 points
    assert result.scores["structure"] == 95


def test_when_to_use_guidance_detection(temp_skill_dir):
    """Test detection of 'when to use' guidance in description."""
    # Missing when-to-use guidance
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: This skill does something useful with data
---

Content.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    assert any(
        "when to use" in f.message.lower()
        for f in result.findings
        if f.category == "clarity"
    )

    # Has when-to-use guidance
    skill_md.write_text(
        """---
name: test-skill
description: Use this skill when you need to process data efficiently
---

Content.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    when_findings = [
        f
        for f in result.findings
        if "when to use" in f.message.lower() and f.category == "clarity"
    ]
    assert len(when_findings) == 0


def test_license_check(temp_skill_dir):
    """Test license field checking."""
    # Without license
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: A skill for testing license detection when evaluating
---

Content.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    assert any(
        "license" in f.message.lower()
        for f in result.findings
        if f.category == "completeness"
    )

    # With license
    skill_md.write_text(
        """---
name: test-skill
description: A skill for testing license detection when evaluating
license: MIT
---

Content.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    license_findings = [
        f
        for f in result.findings
        if "license" in f.message.lower() and f.category == "completeness"
    ]
    assert len(license_findings) == 0


def test_actionable_language_detection(temp_skill_dir):
    """Test detection of actionable language."""
    # Without actionable language
    skill_md = temp_skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: A skill for testing actionable language when evaluating
---

This is some information about the topic.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    assert any(
        "actionable" in f.message.lower()
        for f in result.findings
        if f.category == "clarity"
    )

    # With actionable language
    skill_md.write_text(
        """---
name: test-skill
description: A skill for testing actionable language when evaluating
---

You should always use this approach when working with data.
""",
        encoding="utf-8",
    )

    result = evaluate_skill(temp_skill_dir)
    actionable_findings = [
        f
        for f in result.findings
        if "actionable" in f.message.lower() and f.category == "clarity"
    ]
    assert len(actionable_findings) == 0
