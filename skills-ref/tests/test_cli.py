"""Tests for CLI --allow-field option."""

from click.testing import CliRunner

from skills_ref.cli import main


def test_allow_field_single(tmp_path):
    """Single --allow-field flag suppresses error for that field."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
user-invocable: true
---
Body
""")
    runner = CliRunner()
    result = runner.invoke(
        main, ["validate", "--allow-field", "user-invocable", str(skill_dir)]
    )
    assert result.exit_code == 0


def test_allow_field_empty_value_rejected(tmp_path):
    """Empty --allow-field value produces an error."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
---
Body
""")
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--allow-field", "", str(skill_dir)])
    assert result.exit_code == 1
    assert "invalid --allow-field value" in result.output


def test_allow_field_invalid_characters_rejected(tmp_path):
    """Field names with invalid characters are rejected."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
---
Body
""")
    runner = CliRunner()
    result = runner.invoke(
        main, ["validate", "--allow-field", "User_Invocable", str(skill_dir)]
    )
    assert result.exit_code == 1
    assert "invalid --allow-field value" in result.output
    assert "lowercase ASCII letters separated by single hyphens" in result.output


def test_allow_field_partial_coverage(tmp_path):
    """Fields not covered by --allow-field still cause validation failure."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
user-invocable: true
totally-bogus: wat
---
Body
""")
    runner = CliRunner()
    result = runner.invoke(
        main, ["validate", "--allow-field", "user-invocable", str(skill_dir)]
    )
    assert result.exit_code == 1
    assert "totally-bogus" in result.output


def test_allow_field_mixed_valid_and_invalid(tmp_path):
    """Only invalid values are reported; valid values are not flagged."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
---
Body
""")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "validate",
            "--allow-field",
            "good-name",
            "--allow-field",
            "Bad_Name",
            "--allow-field",
            "also-good",
            "--allow-field",
            "123bad",
            str(skill_dir),
        ],
    )
    assert result.exit_code == 1
    assert "'Bad_Name'" in result.output
    assert "'123bad'" in result.output
    assert "good-name" not in result.output
    assert "also-good" not in result.output


def test_allow_field_with_skill_md_file_path(tmp_path):
    """--allow-field works when user passes a SKILL.md file path."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("""---
name: my-skill
description: A test skill
user-invocable: true
---
Body
""")
    runner = CliRunner()
    result = runner.invoke(
        main, ["validate", "--allow-field", "user-invocable", str(skill_md)]
    )
    assert result.exit_code == 0


def test_allow_field_multiple(tmp_path):
    """Multiple --allow-field flags all work."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
user-invocable: true
model: opus
---
Body
""")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "validate",
            "--allow-field",
            "user-invocable",
            "--allow-field",
            "model",
            str(skill_dir),
        ],
    )
    assert result.exit_code == 0
