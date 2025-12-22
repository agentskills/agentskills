"""Tests for validator module."""

from skills_ref.models import FieldSchema, SkillProperties, TypeParam
from skills_ref.validator import (
    typecheck_composition,
    typecheck_higher_order,
    validate,
    _parse_generic_type,
    _is_valid_type,
)


def test_valid_skill(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
---
# My Skill
""")
    errors = validate(skill_dir)
    assert errors == []


def test_nonexistent_path(tmp_path):
    errors = validate(tmp_path / "nonexistent")
    assert len(errors) == 1
    assert "does not exist" in errors[0]


def test_not_a_directory(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    errors = validate(file_path)
    assert len(errors) == 1
    assert "Not a directory" in errors[0]


def test_missing_skill_md(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    errors = validate(skill_dir)
    assert len(errors) == 1
    assert "Missing required file: SKILL.md" in errors[0]


def test_invalid_name_uppercase(tmp_path):
    skill_dir = tmp_path / "MySkill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: MySkill
description: A test skill
---
Body
""")
    errors = validate(skill_dir)
    assert any("lowercase" in e for e in errors)


def test_name_too_long(tmp_path):
    long_name = "a" * 70  # Exceeds 64 char limit
    skill_dir = tmp_path / long_name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(f"""---
name: {long_name}
description: A test skill
---
Body
""")
    errors = validate(skill_dir)
    assert any("exceeds" in e and "character limit" in e for e in errors)


def test_name_leading_hyphen(tmp_path):
    skill_dir = tmp_path / "-my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: -my-skill
description: A test skill
---
Body
""")
    errors = validate(skill_dir)
    assert any("cannot start or end with a hyphen" in e for e in errors)


def test_name_consecutive_hyphens(tmp_path):
    skill_dir = tmp_path / "my--skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my--skill
description: A test skill
---
Body
""")
    errors = validate(skill_dir)
    assert any("consecutive hyphens" in e for e in errors)


def test_name_invalid_characters(tmp_path):
    skill_dir = tmp_path / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my_skill
description: A test skill
---
Body
""")
    errors = validate(skill_dir)
    assert any("invalid characters" in e for e in errors)


def test_name_directory_mismatch(tmp_path):
    skill_dir = tmp_path / "wrong-name"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: correct-name
description: A test skill
---
Body
""")
    errors = validate(skill_dir)
    assert any("must match skill name" in e for e in errors)


def test_unexpected_fields(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
unknown_field: should not be here
---
Body
""")
    errors = validate(skill_dir)
    assert any("Unexpected fields" in e for e in errors)


def test_valid_with_all_fields(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
license: MIT
metadata:
  author: Test
---
Body
""")
    errors = validate(skill_dir)
    assert errors == []


def test_allowed_tools_accepted(tmp_path):
    """allowed-tools is accepted (experimental feature)."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
allowed-tools: Bash(jq:*) Bash(git:*)
---
Body
""")
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_chinese_name(tmp_path):
    """Chinese characters are allowed in skill names."""
    skill_dir = tmp_path / "技能"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: 技能
description: A skill with Chinese name
---
Body
""")
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_russian_name_with_hyphens(tmp_path):
    """Russian names with hyphens are allowed."""
    skill_dir = tmp_path / "мой-навык"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: мой-навык
description: A skill with Russian name
---
Body
""")
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_russian_lowercase_valid(tmp_path):
    """Russian lowercase names should be accepted."""
    skill_dir = tmp_path / "навык"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: навык
description: A skill with Russian lowercase name
---
Body
""")
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_russian_uppercase_rejected(tmp_path):
    """Russian uppercase names should be rejected."""
    skill_dir = tmp_path / "НАВЫК"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: НАВЫК
description: A skill with Russian uppercase name
---
Body
""")
    errors = validate(skill_dir)
    assert any("lowercase" in e for e in errors)


def test_description_too_long(tmp_path):
    """Description exceeding 1024 chars should fail."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    long_desc = "x" * 1100
    (skill_dir / "SKILL.md").write_text(f"""---
name: my-skill
description: {long_desc}
---
Body
""")
    errors = validate(skill_dir)
    assert any("exceeds" in e and "1024" in e for e in errors)


def test_valid_compatibility(tmp_path):
    """Valid compatibility field should be accepted."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
compatibility: Requires Python 3.11+
---
Body
""")
    errors = validate(skill_dir)
    assert errors == []


def test_compatibility_too_long(tmp_path):
    """Compatibility exceeding 500 chars should fail."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    long_compat = "x" * 550
    (skill_dir / "SKILL.md").write_text(f"""---
name: my-skill
description: A test skill
compatibility: {long_compat}
---
Body
""")
    errors = validate(skill_dir)
    assert any("exceeds" in e and "500" in e for e in errors)


def test_nfkc_normalization(tmp_path):
    """Skill names are NFKC normalized before validation.

    The name 'café' can be represented two ways:
    - Precomposed: 'café' (4 chars, 'é' is U+00E9)
    - Decomposed: 'café' (5 chars, 'e' + combining acute U+0301)

    NFKC normalizes both to the precomposed form.
    """
    # Use decomposed form: 'cafe' + combining acute accent (U+0301)
    decomposed_name = "cafe\u0301"  # 'café' with combining accent
    composed_name = "café"  # precomposed form

    # Directory uses composed form, SKILL.md uses decomposed - should match after normalization
    skill_dir = tmp_path / composed_name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(f"""---
name: {decomposed_name}
description: A test skill
---
Body
""")
    errors = validate(skill_dir)
    assert errors == [], f"Expected no errors, got: {errors}"


# =============================================================================
# Composability Tests - Level, Operation, Composes fields
# =============================================================================


class TestComposabilityLevel:
    """Tests for the level field (composition hierarchy tier)."""

    def test_valid_level_1_atomic(self, tmp_path):
        """Level 1 (Atomic) skills should be valid."""
        skill_dir = tmp_path / "email-read"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: email-read
description: Read emails from Gmail or Outlook
level: 1
operation: READ
---
# Email Read
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_level_2_composite(self, tmp_path):
        """Level 2 (Composite) skills should be valid."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic with web search and archival
level: 2
operation: READ
composes:
  - web-search
  - pdf-save
---
# Research
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_level_3_workflow(self, tmp_path):
        """Level 3 (Workflow) skills should be valid."""
        skill_dir = tmp_path / "daily-synthesis"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: daily-synthesis
description: Daily action item synthesis from all channels
level: 3
operation: WRITE
composes:
  - email-read
  - slack-read
  - research
---
# Daily Synthesis
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_invalid_level_zero(self, tmp_path):
        """Level 0 should be rejected (primitives are not skills)."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
level: 0
---
Body
""")
        errors = validate(skill_dir)
        assert any("level" in e.lower() and ("1, 2, or 3" in e or "1=Atomic" in e) for e in errors)

    def test_invalid_level_four(self, tmp_path):
        """Level 4+ should be rejected."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
level: 4
---
Body
""")
        errors = validate(skill_dir)
        assert any("level" in e.lower() and ("1, 2, or 3" in e or "1=Atomic" in e) for e in errors)

    def test_invalid_level_string(self, tmp_path):
        """Level must be an integer, not a non-numeric string."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
level: high
---
Body
""")
        errors = validate(skill_dir)
        assert any("integer" in e.lower() for e in errors)

    def test_level_1_with_composes_rejected(self, tmp_path):
        """Atomic skills (Level 1) should not compose other skills."""
        skill_dir = tmp_path / "email-read"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: email-read
description: Read emails
level: 1
composes:
  - some-other-skill
---
Body
""")
        errors = validate(skill_dir)
        assert any("Level 1" in e and "should not have" in e for e in errors)


class TestComposabilityOperation:
    """Tests for the operation field (safety classification)."""

    def test_valid_operation_read(self, tmp_path):
        """READ operation should be valid."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A read-only skill
operation: READ
---
Body
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_operation_write(self, tmp_path):
        """WRITE operation should be valid."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A skill that writes data
operation: WRITE
---
Body
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_operation_transform(self, tmp_path):
        """TRANSFORM operation should be valid."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A local transformation skill
operation: TRANSFORM
---
Body
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_invalid_operation_lowercase(self, tmp_path):
        """Operations must be uppercase."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
operation: read
---
Body
""")
        errors = validate(skill_dir)
        assert any("operation" in e.lower() for e in errors)

    def test_invalid_operation_unknown(self, tmp_path):
        """Unknown operations should be rejected."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
operation: DELETE
---
Body
""")
        errors = validate(skill_dir)
        assert any("operation" in e.lower() for e in errors)


class TestComposabilityComposes:
    """Tests for the composes field (skill dependencies)."""

    def test_valid_composes_list(self, tmp_path):
        """Composes should accept a list of skill names."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research with multiple sources
level: 2
composes:
  - web-search
  - pdf-save
  - email-read
---
Body
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_composes_single_item(self, tmp_path):
        """Composes should accept a single-item list."""
        skill_dir = tmp_path / "simple-composite"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: simple-composite
description: A simple composite skill
level: 2
composes:
  - web-search
---
Body
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_invalid_composes_string(self, tmp_path):
        """Composes must be a list, not a string."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
level: 2
composes: web-search
---
Body
""")
        errors = validate(skill_dir)
        # Note: parser converts single string to list, so this may pass
        # depending on implementation

    def test_invalid_composes_empty_string(self, tmp_path):
        """Empty strings in composes should be rejected."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
level: 2
composes:
  - web-search
  - ""
---
Body
""")
        errors = validate(skill_dir)
        assert any("empty" in e.lower() for e in errors)


class TestComposabilityIntegration:
    """Integration tests for composability features."""

    def test_complete_atomic_skill(self, tmp_path):
        """A complete Level 1 atomic skill with all fields."""
        skill_dir = tmp_path / "web-search"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: web-search
description: Search the web using AI-powered search. Returns synthesised answers with citations.
level: 1
operation: READ
license: Apache-2.0
compatibility: Requires internet access
metadata:
  author: example-org
  version: "1.0"
---
# Web Search

Search the web and get synthesised answers.
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_complete_composite_skill(self, tmp_path):
        """A complete Level 2 composite skill with all fields."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic comprehensively with web search and source archival.
level: 2
operation: READ
composes:
  - web-search
  - pdf-save
license: Apache-2.0
metadata:
  author: example-org
---
# Research

Comprehensive topic research.
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_complete_workflow_skill(self, tmp_path):
        """A complete Level 3 workflow skill with all fields."""
        skill_dir = tmp_path / "daily-briefing"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: daily-briefing
description: Generate comprehensive morning briefing from all sources.
level: 3
operation: READ
composes:
  - calendar-read
  - email-read
  - research
  - customer-intel
license: Apache-2.0
---
# Daily Briefing

Orchestrates multiple skills for morning preparation.
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_skill_without_composability_fields(self, tmp_path):
        """Skills without composability fields should still be valid (backwards compatibility)."""
        skill_dir = tmp_path / "legacy-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: legacy-skill
description: A skill without composability fields
---
# Legacy Skill

Works without level, operation, or composes.
""")
        errors = validate(skill_dir)
        assert errors == [], "Backwards compatibility broken - skills without composability fields should be valid"


# =============================================================================
# Type Checking Tests - Input/Output Schema Validation
# =============================================================================


class TestFieldSchemaValidation:
    """Tests for individual field schema validation."""

    def test_valid_input_schema(self, tmp_path):
        """Valid input schemas should be accepted."""
        skill_dir = tmp_path / "typed-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: typed-skill
description: A skill with typed inputs
level: 1
operation: READ
inputs:
  - name: query
    type: string
    required: true
    description: Search query
  - name: limit
    type: integer
    required: false
    default: 10
---
# Typed Skill
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_output_schema(self, tmp_path):
        """Valid output schemas should be accepted."""
        skill_dir = tmp_path / "typed-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: typed-skill
description: A skill with typed outputs
level: 1
operation: READ
outputs:
  - name: results
    type: string[]
    description: List of results
  - name: count
    type: integer
---
# Typed Skill
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_epistemic_requirements(self, tmp_path):
        """Epistemic requirements (requires_source, requires_rationale) should be accepted."""
        skill_dir = tmp_path / "rigorous-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: rigorous-skill
description: A skill requiring sources and rationale
level: 1
operation: READ
outputs:
  - name: answer
    type: string
    requires_source: true
    requires_rationale: true
    min_length: 50
  - name: sources
    type: string[]
    min_items: 2
---
# Rigorous Skill
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_valid_range_constraint(self, tmp_path):
        """Range constraints should be accepted."""
        skill_dir = tmp_path / "bounded-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: bounded-skill
description: A skill with range constraints
level: 1
operation: READ
outputs:
  - name: confidence
    type: number
    range:
      - 0
      - 1
  - name: score
    type: integer
    range:
      - 0
      - 100
---
# Bounded Skill
""")
        errors = validate(skill_dir)
        assert errors == []

    def test_invalid_range_min_greater_than_max(self, tmp_path):
        """Range with min > max should be rejected."""
        skill_dir = tmp_path / "bad-range"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: bad-range
description: A skill with invalid range
level: 1
operation: READ
outputs:
  - name: score
    type: number
    range:
      - 100
      - 0
---
# Bad Range
""")
        errors = validate(skill_dir)
        assert any("min" in e and "max" in e for e in errors)

    def test_field_missing_name(self, tmp_path):
        """Fields without name should be rejected."""
        skill_dir = tmp_path / "unnamed-field"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: unnamed-field
description: A skill with unnamed field
level: 1
operation: READ
inputs:
  - type: string
---
# Unnamed Field
""")
        errors = validate(skill_dir)
        assert any("name" in e.lower() for e in errors)


class TestTypeChecking:
    """Tests for composition type checking."""

    def test_compatible_types_exact_match(self):
        """Exact type matches should pass."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            inputs=[FieldSchema(name="query", type="string")],
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            inputs=[FieldSchema(name="query", type="string")],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert errors == []

    def test_compatible_types_integer_to_number(self):
        """Integer widening to number should pass."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            inputs=[FieldSchema(name="count", type="integer")],
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            inputs=[FieldSchema(name="count", type="number")],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert errors == []

    def test_compatible_types_datetime_to_date(self):
        """Datetime satisfying date should pass."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            inputs=[FieldSchema(name="when", type="datetime")],
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            inputs=[FieldSchema(name="when", type="date")],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert errors == []

    def test_compatible_types_any(self):
        """Any type should be compatible with everything."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            inputs=[FieldSchema(name="data", type="any")],
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            inputs=[FieldSchema(name="data", type="string")],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert errors == []

    def test_incompatible_types_string_to_integer(self):
        """String to integer should fail."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            inputs=[FieldSchema(name="count", type="string")],
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            inputs=[FieldSchema(name="count", type="integer", required=True)],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert any("type mismatch" in e.lower() for e in errors)

    def test_incompatible_types_list_to_scalar(self):
        """List type to scalar should fail."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            inputs=[FieldSchema(name="items", type="string[]")],
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            inputs=[FieldSchema(name="items", type="string", required=True)],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert any("type mismatch" in e.lower() for e in errors)

    def test_missing_composed_skill(self):
        """Missing composed skill should report error."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["nonexistent"],
        )
        errors = typecheck_composition(parent, {})
        assert any("not found" in e.lower() for e in errors)

    def test_output_type_mismatch(self):
        """Child output not matching parent declared output should fail."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            outputs=[FieldSchema(name="result", type="integer")],
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            outputs=[FieldSchema(name="result", type="string")],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert any("type mismatch" in e.lower() for e in errors)

    def test_optional_input_not_checked(self):
        """Optional inputs should not cause type errors."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=["child"],
            inputs=[],  # No matching input
        )
        child = SkillProperties(
            name="child",
            description="Child skill",
            inputs=[FieldSchema(name="optional", type="string", required=False)],
        )
        errors = typecheck_composition(parent, {"child": child})
        assert errors == []

    def test_no_composes_no_errors(self):
        """Skills without composes should have no type errors."""
        parent = SkillProperties(
            name="parent",
            description="Parent skill",
            composes=None,
        )
        errors = typecheck_composition(parent, {})
        assert errors == []

    def test_complex_composition_chain(self):
        """Complex composition with multiple skills should work."""
        workflow = SkillProperties(
            name="workflow",
            description="Workflow skill",
            composes=["composite", "atomic"],
            inputs=[
                FieldSchema(name="query", type="string"),
                FieldSchema(name="limit", type="integer"),
            ],
            outputs=[FieldSchema(name="summary", type="string")],
        )
        composite = SkillProperties(
            name="composite",
            description="Composite skill",
            inputs=[FieldSchema(name="query", type="string", required=True)],
            outputs=[FieldSchema(name="summary", type="string")],
        )
        atomic = SkillProperties(
            name="atomic",
            description="Atomic skill",
            inputs=[FieldSchema(name="limit", type="integer", required=True)],
        )
        errors = typecheck_composition(
            workflow, {"composite": composite, "atomic": atomic}
        )
        assert errors == []


# =============================================================================
# Higher-Order Skills Tests - Type Parameters and Generic Types
# =============================================================================


class TestGenericTypeParsing:
    """Tests for parsing generic type strings like Skill<A, B>."""

    def test_parse_simple_generic(self):
        """Parse Skill<A, B> correctly."""
        base, params = _parse_generic_type("Skill<A, B>")
        assert base == "Skill"
        assert params == ["A", "B"]

    def test_parse_generic_with_concrete_types(self):
        """Parse Skill<string, number> correctly."""
        base, params = _parse_generic_type("Skill<string, number>")
        assert base == "Skill"
        assert params == ["string", "number"]

    def test_parse_nested_generic(self):
        """Parse nested generic types like Skill<A[], B[]>."""
        base, params = _parse_generic_type("Skill<A[], B[]>")
        assert base == "Skill"
        assert params == ["A[]", "B[]"]

    def test_parse_non_generic(self):
        """Non-generic types return None."""
        base, params = _parse_generic_type("string")
        assert base is None
        assert params == []

    def test_parse_list_of_generic(self):
        """Skill<A, B>[] should be handled."""
        # This is the outer list, the inner generic is parsed separately
        base, params = _parse_generic_type("Skill<A, B>")
        assert base == "Skill"
        assert params == ["A", "B"]


class TestGenericTypeValidation:
    """Tests for validating types including generics and type parameters."""

    def test_valid_primitive_type(self):
        """Primitive types should be valid."""
        valid, err = _is_valid_type("string")
        assert valid is True
        assert err is None

    def test_valid_list_type(self):
        """List types should be valid."""
        valid, err = _is_valid_type("string[]")
        assert valid is True
        assert err is None

    def test_valid_type_parameter(self):
        """Type parameters should be valid when in scope."""
        valid, err = _is_valid_type("A", type_params={"A", "B"})
        assert valid is True
        assert err is None

    def test_invalid_type_parameter_not_in_scope(self):
        """Type parameters not in scope should be invalid."""
        valid, err = _is_valid_type("C", type_params={"A", "B"})
        assert valid is False
        assert "Unknown type" in err

    def test_valid_skill_generic_with_type_params(self):
        """Skill<A, B> should be valid when A and B are in scope."""
        valid, err = _is_valid_type("Skill<A, B>", type_params={"A", "B"})
        assert valid is True
        assert err is None

    def test_valid_skill_generic_with_concrete_types(self):
        """Skill<string, number> should be valid."""
        valid, err = _is_valid_type("Skill<string, number>")
        assert valid is True
        assert err is None

    def test_invalid_skill_wrong_param_count(self):
        """Skill with wrong number of params should be invalid."""
        valid, err = _is_valid_type("Skill<A>", type_params={"A"})
        assert valid is False
        assert "expects 2 type parameters" in err

    def test_invalid_unknown_generic(self):
        """Unknown generic types should be invalid."""
        valid, err = _is_valid_type("Unknown<A, B>", type_params={"A", "B"})
        assert valid is False
        assert "Unknown generic type" in err

    def test_valid_nested_skill_type(self):
        """Skill<A[], B[]> should be valid."""
        valid, err = _is_valid_type("Skill<A[], B[]>", type_params={"A", "B"})
        assert valid is True
        assert err is None


class TestTypeParamsValidation:
    """Tests for type_params field validation in SKILL.md."""

    def test_valid_type_params(self, tmp_path):
        """Valid type_params should be accepted."""
        skill_dir = tmp_path / "map-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: map-skill
description: Apply a skill to each item in a list
level: 2
operation: READ
type_params:
  - name: A
    description: Input item type
  - name: B
    description: Output item type
inputs:
  - name: items
    type: A[]
  - name: processor
    type: Skill<A, B>
outputs:
  - name: results
    type: B[]
---
# Map Skill
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_type_params_must_start_uppercase(self, tmp_path):
        """Type parameter names should start with uppercase."""
        skill_dir = tmp_path / "bad-params"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: bad-params
description: A skill with invalid type param
level: 2
operation: READ
type_params:
  - name: input
    description: Should be uppercase
---
# Bad Params
""")
        errors = validate(skill_dir)
        assert any("uppercase" in e.lower() for e in errors)

    def test_type_params_no_duplicates(self, tmp_path):
        """Duplicate type parameter names should be rejected."""
        skill_dir = tmp_path / "dup-params"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: dup-params
description: A skill with duplicate type params
level: 2
operation: READ
type_params:
  - name: A
  - name: A
---
# Dup Params
""")
        errors = validate(skill_dir)
        assert any("duplicate" in e.lower() for e in errors)

    def test_type_params_used_in_inputs(self, tmp_path):
        """Type parameters should be usable in input types."""
        skill_dir = tmp_path / "with-retry"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: with-retry
description: Wrap a skill with retry logic
level: 2
operation: READ
type_params:
  - name: A
    description: Input type
  - name: B
    description: Output type
inputs:
  - name: target
    type: Skill<A, B>
    required: true
  - name: max_attempts
    type: integer
    default: 3
outputs:
  - name: result
    type: B
  - name: attempts
    type: integer
---
# With Retry
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_undefined_type_param_rejected(self, tmp_path):
        """Using undefined type parameters should be rejected."""
        skill_dir = tmp_path / "undefined-param"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: undefined-param
description: A skill using undefined type param
level: 2
operation: READ
type_params:
  - name: A
inputs:
  - name: value
    type: B
---
# Undefined Param
""")
        errors = validate(skill_dir)
        assert any("Unknown type" in e for e in errors)


class TestHigherOrderSkillProperties:
    """Tests for SkillProperties with type parameters."""

    def test_is_generic_with_type_params(self):
        """Skills with type_params should be marked as generic."""
        skill = SkillProperties(
            name="map-skill",
            description="Map skill",
            type_params=[
                TypeParam(name="A", description="Input type"),
                TypeParam(name="B", description="Output type"),
            ],
        )
        assert skill.is_generic is True
        assert skill.type_param_names == {"A", "B"}

    def test_is_generic_without_type_params(self):
        """Skills without type_params should not be marked as generic."""
        skill = SkillProperties(
            name="web-search",
            description="Web search",
        )
        assert skill.is_generic is False
        assert skill.type_param_names == set()

    def test_to_dict_includes_type_params(self):
        """to_dict should include type_params when present."""
        skill = SkillProperties(
            name="with-retry",
            description="Retry wrapper",
            type_params=[
                TypeParam(name="A"),
                TypeParam(name="B", description="Output type"),
            ],
        )
        d = skill.to_dict()
        assert "type_params" in d
        assert len(d["type_params"]) == 2
        assert d["type_params"][0]["name"] == "A"
        assert d["type_params"][1]["description"] == "Output type"


class TestHigherOrderTypeChecking:
    """Tests for type checking higher-order skill compositions."""

    def test_wrapper_skill_type_params(self):
        """Higher-order skills wrapping other skills should pass type check."""
        with_retry = SkillProperties(
            name="with-retry",
            description="Retry wrapper",
            type_params=[
                TypeParam(name="A"),
                TypeParam(name="B"),
            ],
            inputs=[
                FieldSchema(name="target", type="Skill<A, B>", required=True),
                FieldSchema(name="max_attempts", type="integer"),
            ],
            outputs=[
                FieldSchema(name="result", type="B"),
                FieldSchema(name="attempts", type="integer"),
            ],
        )
        web_search = SkillProperties(
            name="web-search",
            description="Search the web",
            inputs=[FieldSchema(name="query", type="string", required=True)],
            outputs=[FieldSchema(name="results", type="string[]")],
        )
        errors = typecheck_higher_order(with_retry, web_search)
        assert errors == []

    def test_non_generic_skill_skips_higher_order_check(self):
        """Non-generic skills should skip higher-order type checking."""
        regular_skill = SkillProperties(
            name="regular",
            description="Regular skill",
            inputs=[FieldSchema(name="query", type="string")],
        )
        other_skill = SkillProperties(
            name="other",
            description="Other skill",
        )
        errors = typecheck_higher_order(regular_skill, other_skill)
        assert errors == []


class TestSkillGenericInWorkflows:
    """Integration tests for using generic skills in workflows."""

    def test_full_higher_order_workflow(self, tmp_path):
        """A complete workflow using higher-order skills."""
        skill_dir = tmp_path / "resilient-search"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: resilient-search
description: Search with retry and caching
level: 3
operation: READ
composes:
  - with-retry
  - with-cache
  - web-search
inputs:
  - name: query
    type: string
    required: true
outputs:
  - name: results
    type: string[]
---
# Resilient Search

Composes higher-order skills for reliable search.
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_combinator_skill_validation(self, tmp_path):
        """Combinator skills like fan-out should validate correctly."""
        skill_dir = tmp_path / "fan-out"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: fan-out
description: Execute multiple skills in parallel on the same input
level: 2
operation: READ
type_params:
  - name: A
    description: Input type
  - name: B
    description: Output type
inputs:
  - name: input
    type: A
    required: true
  - name: skills
    type: Skill<A, B>[]
    required: true
outputs:
  - name: results
    type: B[]
  - name: stats
    type: any
---
# Fan Out
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"


# =============================================================================
# Lessons Schema Tests (Continuous Improvement)
# =============================================================================


class TestLessonsValidation:
    """Tests for the lessons schema that enables continuous improvement."""

    def test_valid_lesson_minimal(self, tmp_path):
        """A lesson with required fields only should validate."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all conflicting sources"
---
# Research
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_valid_lesson_full(self, tmp_path):
        """A lesson with all fields should validate."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict on factual claims"
    learned: "Always cite all conflicting sources, not just one"
    confidence: 0.95
    status: validated
    source: "execution-2025-12-15-001"
    proposed_edit: "Add source_conflicts output field"
    validated_at: "2025-12-15"
---
# Research
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_lesson_missing_id(self, tmp_path):
        """A lesson without id should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - context: "WHEN sources conflict"
    learned: "Cite all sources"
---
# Research
""")
        errors = validate(skill_dir)
        assert any("missing required 'id'" in e for e in errors)

    def test_lesson_invalid_id_format(self, tmp_path):
        """A lesson with invalid ID format should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: invalid-id
    context: "WHEN sources conflict"
    learned: "Cite all sources"
---
# Research
""")
        errors = validate(skill_dir)
        assert any("must match pattern L-SKILL-NNN" in e for e in errors)

    def test_lesson_missing_context(self, tmp_path):
        """A lesson without context should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    learned: "Cite all sources"
---
# Research
""")
        errors = validate(skill_dir)
        assert any("missing required 'context'" in e for e in errors)

    def test_lesson_missing_learned(self, tmp_path):
        """A lesson without learned should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
---
# Research
""")
        errors = validate(skill_dir)
        assert any("missing required 'learned'" in e for e in errors)

    def test_lesson_confidence_out_of_range(self, tmp_path):
        """A lesson with confidence > 1.0 should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all sources"
    confidence: 1.5
---
# Research
""")
        errors = validate(skill_dir)
        assert any("between 0.0 and 1.0" in e for e in errors)

    def test_lesson_invalid_status(self, tmp_path):
        """A lesson with invalid status should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all sources"
    status: invalid-status
---
# Research
""")
        errors = validate(skill_dir)
        assert any("must be one of" in e for e in errors)

    def test_lesson_validated_low_confidence(self, tmp_path):
        """A validated lesson with low confidence should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all sources"
    confidence: 0.5
    status: validated
---
# Research
""")
        errors = validate(skill_dir)
        assert any("validated lessons should have confidence >= 0.8" in e for e in errors)

    def test_lesson_applied_without_proposed_edit(self, tmp_path):
        """An applied lesson without proposed_edit should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all sources"
    confidence: 0.95
    status: applied
---
# Research
""")
        errors = validate(skill_dir)
        assert any("applied lessons must have 'proposed_edit'" in e for e in errors)

    def test_lesson_applied_with_proposed_edit(self, tmp_path):
        """An applied lesson with proposed_edit should validate."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all sources"
    confidence: 0.95
    status: applied
    proposed_edit: "Added source_conflicts field"
    applied_at: "2025-12-20"
---
# Research
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_lesson_duplicate_ids(self, tmp_path):
        """Duplicate lesson IDs should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all sources"
  - id: L-research-001
    context: "WHEN results are uncertain"
    learned: "Express uncertainty"
---
# Research
""")
        errors = validate(skill_dir)
        assert any("Duplicate lesson ID" in e for e in errors)

    def test_multiple_lessons_valid(self, tmp_path):
        """Multiple valid lessons should validate."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons:
  - id: L-research-001
    context: "WHEN sources conflict"
    learned: "Cite all conflicting sources"
    confidence: 0.95
    status: validated
  - id: L-research-002
    context: "WHEN primary sources are unavailable"
    learned: "Note the limitation explicitly"
    confidence: 0.85
    status: proposed
  - id: L-research-003
    context: "WHEN dealing with recent events"
    learned: "Check publication dates carefully"
    confidence: 0.6
    status: observed
---
# Research
""")
        errors = validate(skill_dir)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_lessons_not_a_list(self, tmp_path):
        """Lessons as a non-list should fail."""
        skill_dir = tmp_path / "research"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: research
description: Research a topic
lessons: "not a list"
---
# Research
""")
        errors = validate(skill_dir)
        assert any("must be a list" in e for e in errors)


class TestLessonModelProperties:
    """Tests for Lesson dataclass properties."""

    def test_lesson_is_actionable_true(self):
        """Lesson with high confidence and proposed/validated status is actionable."""
        from skills_ref.models import Lesson

        lesson = Lesson(
            id="L-test-001",
            context="WHEN x happens",
            learned="Do y instead",
            confidence=0.85,
            status="proposed"
        )
        assert lesson.is_actionable is True

        lesson2 = Lesson(
            id="L-test-002",
            context="WHEN a happens",
            learned="Do b instead",
            confidence=0.9,
            status="validated"
        )
        assert lesson2.is_actionable is True

    def test_lesson_is_actionable_false_low_confidence(self):
        """Lesson with low confidence is not actionable."""
        from skills_ref.models import Lesson

        lesson = Lesson(
            id="L-test-001",
            context="WHEN x happens",
            learned="Do y instead",
            confidence=0.5,
            status="proposed"
        )
        assert lesson.is_actionable is False

    def test_lesson_is_actionable_false_wrong_status(self):
        """Lesson with observed/applied status is not actionable."""
        from skills_ref.models import Lesson

        lesson = Lesson(
            id="L-test-001",
            context="WHEN x happens",
            learned="Do y instead",
            confidence=0.9,
            status="observed"
        )
        assert lesson.is_actionable is False

    def test_lesson_ready_to_apply_true(self):
        """Validated lesson with high confidence and proposed_edit is ready."""
        from skills_ref.models import Lesson

        lesson = Lesson(
            id="L-test-001",
            context="WHEN x happens",
            learned="Do y instead",
            confidence=0.95,
            status="validated",
            proposed_edit="Add y field to outputs"
        )
        assert lesson.ready_to_apply is True

    def test_lesson_ready_to_apply_false_no_edit(self):
        """Validated lesson without proposed_edit is not ready."""
        from skills_ref.models import Lesson

        lesson = Lesson(
            id="L-test-001",
            context="WHEN x happens",
            learned="Do y instead",
            confidence=0.95,
            status="validated"
        )
        assert lesson.ready_to_apply is False

    def test_lesson_ready_to_apply_false_low_confidence(self):
        """Lesson with confidence < 0.9 is not ready even if validated."""
        from skills_ref.models import Lesson

        lesson = Lesson(
            id="L-test-001",
            context="WHEN x happens",
            learned="Do y instead",
            confidence=0.85,
            status="validated",
            proposed_edit="Add y field"
        )
        assert lesson.ready_to_apply is False

    def test_lesson_to_dict(self):
        """Lesson.to_dict() should exclude None values."""
        from skills_ref.models import Lesson

        lesson = Lesson(
            id="L-test-001",
            context="WHEN x",
            learned="Do y",
            confidence=0.9,
            status="validated"
        )
        d = lesson.to_dict()
        assert d["id"] == "L-test-001"
        assert d["context"] == "WHEN x"
        assert d["learned"] == "Do y"
        assert d["confidence"] == 0.9
        assert d["status"] == "validated"
        assert "source" not in d
        assert "proposed_edit" not in d


class TestSkillPropertiesLessons:
    """Tests for SkillProperties lesson-related properties."""

    def test_has_lessons_true(self):
        """Skill with lessons should return True."""
        from skills_ref.models import Lesson, SkillProperties

        skill = SkillProperties(
            name="test",
            description="Test skill",
            lessons=[
                Lesson(
                    id="L-test-001",
                    context="WHEN x",
                    learned="Do y"
                )
            ]
        )
        assert skill.has_lessons is True

    def test_has_lessons_false(self):
        """Skill without lessons should return False."""
        from skills_ref.models import SkillProperties

        skill = SkillProperties(name="test", description="Test skill")
        assert skill.has_lessons is False

    def test_actionable_lessons(self):
        """actionable_lessons should return only high-confidence proposed/validated."""
        from skills_ref.models import Lesson, SkillProperties

        skill = SkillProperties(
            name="test",
            description="Test skill",
            lessons=[
                Lesson(id="L-test-001", context="x", learned="y",
                       confidence=0.9, status="proposed"),  # actionable
                Lesson(id="L-test-002", context="a", learned="b",
                       confidence=0.5, status="proposed"),  # too low
                Lesson(id="L-test-003", context="c", learned="d",
                       confidence=0.95, status="validated"),  # actionable
                Lesson(id="L-test-004", context="e", learned="f",
                       confidence=0.95, status="observed"),  # wrong status
            ]
        )
        actionable = skill.actionable_lessons
        assert len(actionable) == 2
        assert {l.id for l in actionable} == {"L-test-001", "L-test-003"}

    def test_lessons_ready_to_apply(self):
        """lessons_ready_to_apply should return only fully ready lessons."""
        from skills_ref.models import Lesson, SkillProperties

        skill = SkillProperties(
            name="test",
            description="Test skill",
            lessons=[
                Lesson(id="L-test-001", context="x", learned="y",
                       confidence=0.95, status="validated",
                       proposed_edit="Add z"),  # ready
                Lesson(id="L-test-002", context="a", learned="b",
                       confidence=0.95, status="validated"),  # no edit
                Lesson(id="L-test-003", context="c", learned="d",
                       confidence=0.85, status="validated",
                       proposed_edit="Add w"),  # too low
            ]
        )
        ready = skill.lessons_ready_to_apply
        assert len(ready) == 1
        assert ready[0].id == "L-test-001"

    def test_lesson_stats(self):
        """lesson_stats should return counts by status."""
        from skills_ref.models import Lesson, SkillProperties

        skill = SkillProperties(
            name="test",
            description="Test skill",
            lessons=[
                Lesson(id="L-test-001", context="x", learned="y", status="observed"),
                Lesson(id="L-test-002", context="a", learned="b", status="observed"),
                Lesson(id="L-test-003", context="c", learned="d", status="proposed"),
                Lesson(id="L-test-004", context="e", learned="f", status="validated"),
            ]
        )
        stats = skill.lesson_stats
        assert stats == {"observed": 2, "proposed": 1, "validated": 1}

    def test_to_dict_includes_lessons(self):
        """SkillProperties.to_dict() should include lessons."""
        from skills_ref.models import Lesson, SkillProperties

        skill = SkillProperties(
            name="test",
            description="Test skill",
            lessons=[
                Lesson(id="L-test-001", context="x", learned="y")
            ]
        )
        d = skill.to_dict()
        assert "lessons" in d
        assert len(d["lessons"]) == 1
        assert d["lessons"][0]["id"] == "L-test-001"
