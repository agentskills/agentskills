"""Tests for the models module."""

from skills_ref.models import SkillProperties


def test_to_dict_omits_empty_optionals():
    props = SkillProperties(name="demo", description="Demo skill")

    result = props.to_dict()

    assert result == {"name": "demo", "description": "Demo skill"}
    assert "license" not in result
    assert "compatibility" not in result
    assert "allowed-tools" not in result
    assert "metadata" not in result


def test_to_dict_includes_optional_fields():
    props = SkillProperties(
        name="demo",
        description="Demo skill",
        license="MIT",
        compatibility="Claude 3.5",
        allowed_tools="Bash(*)",
        metadata={"author": "tester"},
    )

    result = props.to_dict()

    assert result["license"] == "MIT"
    assert result["compatibility"] == "Claude 3.5"
    assert result["allowed-tools"] == "Bash(*)"
    assert result["metadata"] == {"author": "tester"}
