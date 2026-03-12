"""Tests for feature flags support."""

import pytest

from skills_ref.models import FeatureDefinition, Features
from skills_ref.parser import read_properties
from skills_ref.validator import validate


# --- Model tests ---


def test_feature_definition_to_dict_minimal():
    feat = FeatureDefinition(description="Test", section="## Test")
    assert feat.to_dict() == {"description": "Test", "section": "## Test"}


def test_feature_definition_to_dict_with_requires():
    feat = FeatureDefinition(description="Test", section="## Test", requires=["other"])
    assert feat.to_dict() == {
        "description": "Test",
        "section": "## Test",
        "requires": ["other"],
    }


def test_features_to_dict_minimal():
    features = Features(
        default=["a"],
        available={"a": FeatureDefinition(description="A", section="## A")},
    )
    result = features.to_dict()
    assert result == {
        "default": ["a"],
        "available": {"a": {"description": "A", "section": "## A"}},
    }


def test_features_to_dict_with_conflicts():
    features = Features(
        default=["a"],
        available={
            "a": FeatureDefinition(description="A", section="## A"),
            "b": FeatureDefinition(description="B", section="## B"),
        },
        conflicts=[["a", "b"]],
    )
    result = features.to_dict()
    assert result["conflicts"] == [["a", "b"]]


# --- Parser tests ---


def test_read_properties_with_features(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - app-router\n"
        "  available:\n"
        "    app-router:\n"
        "      description: App Router patterns\n"
        '      section: "## App Router"\n'
        "    pages-router:\n"
        "      description: Pages Router patterns\n"
        '      section: "## Pages Router"\n'
        "      requires:\n"
        "        - app-router\n"
        "---\n"
        "# My Skill\n"
    )
    props = read_properties(skill_dir)
    assert props.features is not None
    assert props.features.default == ["app-router"]
    assert "app-router" in props.features.available
    assert "pages-router" in props.features.available
    assert props.features.available["pages-router"].requires == ["app-router"]


def test_read_properties_with_features_and_conflicts(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "  available:\n"
        "    a:\n"
        "      description: Feature A\n"
        '      section: "## A"\n'
        "    b:\n"
        "      description: Feature B\n"
        '      section: "## B"\n'
        "  conflicts:\n"
        "    -\n"
        "      - a\n"
        "      - b\n"
        "---\n"
        "Body\n"
    )
    props = read_properties(skill_dir)
    assert props.features.conflicts == [["a", "b"]]


def test_read_properties_without_features(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A test skill
---
Body
""")
    props = read_properties(skill_dir)
    assert props.features is None


def test_read_properties_features_in_to_dict(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "  available:\n"
        "    a:\n"
        "      description: Feature A\n"
        '      section: "## A"\n'
        "---\n"
        "Body\n"
    )
    props = read_properties(skill_dir)
    d = props.to_dict()
    assert "features" in d
    assert d["features"]["default"] == ["a"]
    assert d["features"]["available"]["a"]["description"] == "Feature A"


def test_read_properties_single_default_as_string(tmp_path):
    """A single default feature can be specified as a string."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default: app-router\n"
        "  available:\n"
        "    app-router:\n"
        "      description: App Router patterns\n"
        '      section: "## App Router"\n'
        "---\n"
        "Body\n"
    )
    props = read_properties(skill_dir)
    assert props.features.default == ["app-router"]


# --- Validator tests ---


def test_valid_features(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - app-router\n"
        "  available:\n"
        "    app-router:\n"
        "      description: App Router patterns\n"
        '      section: "## App Router"\n'
        "    pages-router:\n"
        "      description: Pages Router patterns\n"
        '      section: "## Pages Router"\n'
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert errors == []


def test_features_with_requires_and_conflicts(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - app-router\n"
        "    - typescript\n"
        "  available:\n"
        "    app-router:\n"
        "      description: App Router\n"
        '      section: "## App Router"\n'
        "    pages-router:\n"
        "      description: Pages Router\n"
        '      section: "## Pages Router"\n'
        "    typescript:\n"
        "      description: TypeScript\n"
        '      section: "## TypeScript"\n'
        "    i18n:\n"
        "      description: i18n\n"
        '      section: "## i18n"\n'
        "      requires:\n"
        "        - app-router\n"
        "  conflicts:\n"
        "    -\n"
        "      - app-router\n"
        "      - pages-router\n"
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert errors == []


def test_features_missing_default(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  available:\n"
        "    a:\n"
        "      description: A\n"
        '      section: "## A"\n'
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert any("features.default" in e for e in errors)


def test_features_missing_available(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert any("features.available" in e for e in errors)


def test_features_default_references_unknown(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - nonexistent\n"
        "  available:\n"
        "    a:\n"
        "      description: A\n"
        '      section: "## A"\n'
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert any("nonexistent" in e and "not defined" in e for e in errors)


def test_features_requires_unknown_feature(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "  available:\n"
        "    a:\n"
        "      description: A\n"
        '      section: "## A"\n'
        "      requires:\n"
        "        - nonexistent\n"
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert any("requires unknown feature 'nonexistent'" in e for e in errors)


def test_features_conflict_references_unknown(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "  available:\n"
        "    a:\n"
        "      description: A\n"
        '      section: "## A"\n'
        "  conflicts:\n"
        "    -\n"
        "      - a\n"
        "      - nonexistent\n"
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert any("unknown feature 'nonexistent'" in e for e in errors)


def test_feature_missing_description(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "  available:\n"
        "    a:\n"
        '      section: "## A"\n'
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert any("missing required field 'description'" in e for e in errors)


def test_feature_missing_section(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "  available:\n"
        "    a:\n"
        "      description: A\n"
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert any("missing required field 'section'" in e for e in errors)


def test_features_field_accepted_by_validator(tmp_path):
    """Ensure 'features' is in ALLOWED_FIELDS and doesn't trigger unexpected fields error."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: my-skill\n"
        "description: A test skill\n"
        "features:\n"
        "  default:\n"
        "    - a\n"
        "  available:\n"
        "    a:\n"
        "      description: A\n"
        '      section: "## A"\n'
        "---\n"
        "Body\n"
    )
    errors = validate(skill_dir)
    assert not any("Unexpected fields" in e for e in errors)
