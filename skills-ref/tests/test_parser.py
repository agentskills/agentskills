"""Tests for parser module."""

import pytest

from skills_ref.parser import (
    ParseError,
    ValidationError,
    find_skill_md,
    parse_frontmatter,
    read_properties,
)


def test_valid_frontmatter():
    content = """---
name: my-skill
description: A test skill
---
# My Skill

Instructions here.
"""
    metadata, body = parse_frontmatter(content)
    assert metadata["name"] == "my-skill"
    assert metadata["description"] == "A test skill"
    assert "# My Skill" in body


def test_missing_frontmatter():
    content = "# No frontmatter here"
    with pytest.raises(ParseError, match="must start with YAML frontmatter"):
        parse_frontmatter(content)


def test_unclosed_frontmatter():
    content = """---
name: my-skill
description: A test skill
"""
    with pytest.raises(ParseError, match="not properly closed"):
        parse_frontmatter(content)


def test_invalid_yaml():
    content = """---
name: [invalid
description: broken
---
Body here
"""
    with pytest.raises(ParseError, match="Invalid YAML"):
        parse_frontmatter(content)


def test_non_dict_frontmatter():
    content = """---
- just
- a
- list
---
Body
"""
    with pytest.raises(ParseError, match="must be a YAML mapping"):
        parse_frontmatter(content)


def test_read_valid_skill(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
license: MIT
---
# My Skill
""")
    props = read_properties(skill_dir)
    assert props.name == "my-skill"
    assert props.description == "A test skill"
    assert props.license == "MIT"


def test_read_with_metadata(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
metadata:
  author: Test Author
  version: 1.0
---
Body
""")
    props = read_properties(skill_dir)
    assert props.metadata == {"author": "Test Author", "version": "1.0"}


def test_missing_skill_md(tmp_path):
    with pytest.raises(ParseError, match="SKILL.md not found"):
        read_properties(tmp_path)


def test_missing_name(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
description: A test skill
---
Body
""")
    with pytest.raises(ValidationError, match="Missing required field.*name"):
        read_properties(skill_dir)


def test_missing_description(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
---
Body
""")
    with pytest.raises(ValidationError, match="Missing required field.*description"):
        read_properties(skill_dir)


def test_find_skill_md_prefers_uppercase(tmp_path):
    """SKILL.md should be preferred over skill.md when both exist."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("uppercase")
    (skill_dir / "skill.md").write_text("lowercase")
    result = find_skill_md(skill_dir)
    assert result is not None
    assert result.name == "SKILL.md"


def test_find_skill_md_accepts_lowercase(tmp_path):
    """skill.md should be accepted when SKILL.md doesn't exist."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.md").write_text("lowercase")
    result = find_skill_md(skill_dir)
    assert result is not None
    # Check case-insensitively since some filesystems are case-insensitive
    assert result.name.lower() == "skill.md"


def test_find_skill_md_returns_none_when_missing(tmp_path):
    """find_skill_md should return None when no skill.md exists."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    result = find_skill_md(skill_dir)
    assert result is None


def test_read_properties_with_lowercase_skill_md(tmp_path):
    """read_properties should work with lowercase skill.md."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.md").write_text("""---
name: my-skill
description: A test skill
---
# My Skill
""")
    props = read_properties(skill_dir)
    assert props.name == "my-skill"
    assert props.description == "A test skill"


def test_read_with_allowed_tools(tmp_path):
    """allowed-tools should be parsed into SkillProperties."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
allowed-tools: Bash(jq:*) Bash(git:*)
---
Body
""")
    props = read_properties(skill_dir)
    assert props.allowed_tools == "Bash(jq:*) Bash(git:*)"
    # Verify to_dict outputs as "allowed-tools" (hyphenated)
    d = props.to_dict()
    assert d["allowed-tools"] == "Bash(jq:*) Bash(git:*)"


def test_read_with_credentials(tmp_path):
    """credentials should be parsed into SkillProperties."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
credentials:
  - name: OPENAI_API_KEY
    description: OpenAI API key for model access
  - name: SLACK_WEBHOOK_URL
    description: Slack webhook for notifications
    required: false
---
Body
""")
    props = read_properties(skill_dir)
    assert props.credentials is not None
    assert len(props.credentials) == 2
    assert props.credentials[0].name == "OPENAI_API_KEY"
    assert props.credentials[0].description == "OpenAI API key for model access"
    assert props.credentials[0].required is True
    assert props.credentials[1].name == "SLACK_WEBHOOK_URL"
    assert props.credentials[1].required is False
    # Verify to_dict round-trip
    d = props.to_dict()
    assert len(d["credentials"]) == 2
    assert d["credentials"][0] == {
        "name": "OPENAI_API_KEY",
        "description": "OpenAI API key for model access",
    }
    assert d["credentials"][1] == {
        "name": "SLACK_WEBHOOK_URL",
        "description": "Slack webhook for notifications",
        "required": False,
    }


def test_read_without_credentials(tmp_path):
    """Missing credentials should result in None."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
---
Body
""")
    props = read_properties(skill_dir)
    assert props.credentials is None
    d = props.to_dict()
    assert "credentials" not in d
