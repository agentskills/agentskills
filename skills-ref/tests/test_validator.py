"""Tests for validator module."""

from skills_ref.validator import validate


def test_valid_skill(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: my-skill
description: A test skill
---
# My Skill
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == []


def test_nonexistent_path(tmp_path):
    errors = validate(tmp_path / "nonexistent")
    assert len(errors) == 1
    assert "does not exist" in errors[0]


def test_not_a_directory(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("test", encoding="utf-8")
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
    (skill_dir / "SKILL.md").write_text(
        """---
name: MySkill
description: A test skill
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("lowercase" in e for e in errors)


def test_name_too_long(tmp_path):
    long_name = "a" * 70  # Exceeds 64 char limit
    skill_dir = tmp_path / long_name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {long_name}
description: A test skill
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("exceeds" in e and "character limit" in e for e in errors)


def test_name_leading_hyphen(tmp_path):
    skill_dir = tmp_path / "-my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: -my-skill
description: A test skill
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("cannot start or end with a hyphen" in e for e in errors)


def test_name_consecutive_hyphens(tmp_path):
    skill_dir = tmp_path / "my--skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: my--skill
description: A test skill
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("consecutive hyphens" in e for e in errors)


def test_name_invalid_characters(tmp_path):
    skill_dir = tmp_path / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: my_skill
description: A test skill
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("invalid characters" in e for e in errors)


def test_name_directory_mismatch(tmp_path):
    skill_dir = tmp_path / "wrong-name"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: correct-name
description: A test skill
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("must match skill name" in e for e in errors)


def test_unexpected_fields(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: my-skill
description: A test skill
unknown_field: should not be here
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("Unexpected fields" in e for e in errors)


def test_valid_with_all_fields(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: my-skill
description: A test skill
license: MIT
metadata:
  author: Test
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == []


def test_allowed_tools_accepted(tmp_path):
    """allowed-tools is accepted (experimental feature)."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: my-skill
description: A test skill
allowed-tools: Bash(jq:*) Bash(git:*)
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_chinese_name(tmp_path):
    """Chinese characters are allowed in skill names."""
    skill_dir = tmp_path / "技能"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: 技能
description: A skill with Chinese name
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_russian_name_with_hyphens(tmp_path):
    """Russian names with hyphens are allowed."""
    skill_dir = tmp_path / "мой-навык"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: мой-навык
description: A skill with Russian name
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_russian_lowercase_valid(tmp_path):
    """Russian lowercase names should be accepted."""
    skill_dir = tmp_path / "навык"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: навык
description: A skill with Russian lowercase name
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == []


def test_i18n_russian_uppercase_rejected(tmp_path):
    """Russian uppercase names should be rejected."""
    skill_dir = tmp_path / "НАВЫК"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: НАВЫК
description: A skill with Russian uppercase name
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("lowercase" in e for e in errors)


def test_description_too_long(tmp_path):
    """Description exceeding 1024 chars should fail."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    long_desc = "x" * 1100
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: my-skill
description: {long_desc}
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("exceeds" in e and "1024" in e for e in errors)


def test_valid_compatibility(tmp_path):
    """Valid compatibility field should be accepted."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: my-skill
description: A test skill
compatibility: Requires Python 3.11+
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == []


def test_compatibility_too_long(tmp_path):
    """Compatibility exceeding 500 chars should fail."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    long_compat = "x" * 550
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: my-skill
description: A test skill
compatibility: {long_compat}
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert any("exceeds" in e and "500" in e for e in errors)


def test_utf8_skill_md_with_non_cp1252_byte(tmp_path):
    """Regression: SKILL.md containing UTF-8 bytes undefined in CP1252 must validate.

    On Windows, ``Path.read_text()`` defaults to the system locale encoding (CP1252),
    which is undefined for byte ``0x8f`` and several others appearing inside multi-byte
    UTF-8 sequences. Skills authored in real-world UTF-8 (em dashes, hourglass emoji,
    other code points) crashed validation on Windows. The validator must read SKILL.md
    explicitly as UTF-8.
    """
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    # ⏳ (U+23F3) encodes as 0xe2 0x8f 0xb3 — the middle byte 0x8f is undefined in
    # CP1252, so the legacy default-encoding read crashes. Em dash and arrow are
    # CP1252-defined but get mojibake'd if read as CP1252; UTF-8 round-trips them.
    (skill_dir / "SKILL.md").write_text(
        """---
name: my-skill
description: A skill — pending ⏳ → done.
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == [], f"Expected no errors, got: {errors}"


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
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {decomposed_name}
description: A test skill
---
Body
""",
        encoding="utf-8",
    )
    errors = validate(skill_dir)
    assert errors == [], f"Expected no errors, got: {errors}"
