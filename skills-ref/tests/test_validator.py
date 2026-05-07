"""Tests for validator module."""

import json

from skills_ref.validator import validate, validate_evals


def write_valid_skill(skill_dir):
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
---
# My Skill
""")


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


def test_validate_evals_accepts_valid_evals_file(tmp_path):
    skill_dir = tmp_path / "my-skill"
    write_valid_skill(skill_dir)
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir()
    (evals_dir / "evals.json").write_text(json.dumps({
        "skill_name": "my-skill",
        "evals": [
            {
                "id": "chart",
                "prompt": "Create a chart from sales.csv",
                "expected_output": "A labeled chart",
                "files": ["evals/files/sales.csv"],
                "assertions": ["The chart has labeled axes"],
            }
        ],
    }))

    assert validate_evals(skill_dir) == []
    assert validate(skill_dir, include_evals=True) == []


def test_validate_does_not_require_evals_by_default(tmp_path):
    skill_dir = tmp_path / "my-skill"
    write_valid_skill(skill_dir)

    assert validate(skill_dir) == []
    assert validate(skill_dir, include_evals=True) == [
        "Missing optional evals file requested for validation: evals/evals.json"
    ]


def test_validate_evals_rejects_invalid_json(tmp_path):
    skill_dir = tmp_path / "my-skill"
    write_valid_skill(skill_dir)
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir()
    (evals_dir / "evals.json").write_text("{")

    errors = validate_evals(skill_dir)

    assert len(errors) == 1
    assert "Invalid JSON in evals/evals.json" in errors[0]


def test_validate_evals_rejects_missing_required_fields(tmp_path):
    skill_dir = tmp_path / "my-skill"
    write_valid_skill(skill_dir)
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir()
    (evals_dir / "evals.json").write_text(json.dumps({
        "skill_name": "",
        "evals": [
            {
                "id": "",
                "prompt": "",
                "files": ["evals/files/input.csv", ""],
                "assertions": "not a list",
            }
        ],
    }))

    errors = validate_evals(skill_dir)

    assert "Field 'skill_name' must be a non-empty string" in errors
    assert "Field 'evals[0].id' must be a non-empty string or integer" in errors
    assert "Field 'evals[0].prompt' must be a non-empty string" in errors
    assert "Field 'evals[0].expected_output' must be a non-empty string" in errors
    assert "Field 'evals[0].files[1]' must be a non-empty string" in errors
    assert "Field 'evals[0].assertions' must be a list of strings" in errors


def test_validate_evals_rejects_duplicate_ids(tmp_path):
    skill_dir = tmp_path / "my-skill"
    write_valid_skill(skill_dir)
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir()
    (evals_dir / "evals.json").write_text(json.dumps({
        "skill_name": "my-skill",
        "evals": [
            {
                "id": 1,
                "prompt": "First prompt",
                "expected_output": "First output",
            },
            {
                "id": 1,
                "prompt": "Second prompt",
                "expected_output": "Second output",
            },
        ],
    }))

    errors = validate_evals(skill_dir)

    assert "Field 'evals[1].id' must be unique" in errors
