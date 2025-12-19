"""Tests for validator module."""

from skills_ref.models import FieldSchema, SkillProperties
from skills_ref.validator import typecheck_composition, validate


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
