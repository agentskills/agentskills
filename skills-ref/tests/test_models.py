"""Tests for models module."""

from skills_ref.models import SkillProperties


class TestToDict:
    """Tests for SkillProperties.to_dict() method."""

    def test_to_dict_omits_empty_optionals(self):
        """Optional fields should be excluded when not set."""
        props = SkillProperties(name="my-skill", description="A test skill")
        result = props.to_dict()

        assert result == {"name": "my-skill", "description": "A test skill"}
        assert "license" not in result
        assert "compatibility" not in result
        assert "allowed-tools" not in result
        assert "metadata" not in result

    def test_to_dict_includes_optional_fields(self):
        """Optional fields should be included when set."""
        props = SkillProperties(
            name="my-skill",
            description="A test skill",
            license="MIT",
            compatibility="Python 3.11+",
            allowed_tools="Bash(git:*)",
            metadata={"author": "Test"},
        )
        result = props.to_dict()

        assert result["name"] == "my-skill"
        assert result["description"] == "A test skill"
        assert result["license"] == "MIT"
        assert result["compatibility"] == "Python 3.11+"
        assert result["allowed-tools"] == "Bash(git:*)"
        assert result["metadata"] == {"author": "Test"}

    def test_to_dict_required_fields_always_present(self):
        """Required fields (name, description) must always be in output."""
        # With no optional fields
        props_minimal = SkillProperties(name="minimal", description="Minimal skill")
        result_minimal = props_minimal.to_dict()
        assert "name" in result_minimal
        assert "description" in result_minimal

        # With all optional fields
        props_full = SkillProperties(
            name="full",
            description="Full skill",
            license="MIT",
            compatibility="Any",
            allowed_tools="Bash(*)",
            metadata={"key": "value"},
        )
        result_full = props_full.to_dict()
        assert "name" in result_full
        assert "description" in result_full

    def test_to_dict_hyphenated_allowed_tools_key(self):
        """allowed_tools attribute maps to 'allowed-tools' key (snake_case to kebab-case)."""
        props = SkillProperties(
            name="tool-skill",
            description="Has tools",
            allowed_tools="Read Write Edit",
        )
        result = props.to_dict()

        # Must use hyphenated key, not snake_case
        assert "allowed-tools" in result
        assert "allowed_tools" not in result
        assert result["allowed-tools"] == "Read Write Edit"

    def test_to_dict_empty_metadata_excluded(self):
        """Empty metadata dict should be excluded from output."""
        props = SkillProperties(
            name="my-skill",
            description="A test skill",
            metadata={},
        )
        result = props.to_dict()

        assert "metadata" not in result

    def test_to_dict_metadata_with_multiple_entries(self):
        """Metadata with multiple key-value pairs should be preserved."""
        props = SkillProperties(
            name="rich-skill",
            description="Has rich metadata",
            metadata={
                "author": "Test Author",
                "version": "1.0.0",
                "homepage": "https://example.com",
            },
        )
        result = props.to_dict()

        assert result["metadata"] == {
            "author": "Test Author",
            "version": "1.0.0",
            "homepage": "https://example.com",
        }

    def test_to_dict_unicode_values(self):
        """Unicode characters in fields should be preserved."""
        props = SkillProperties(
            name="i18n-skill",
            description="Supports 日本語, русский, and émojis 🎉",
            metadata={"作者": "テスト"},
        )
        result = props.to_dict()

        assert result["description"] == "Supports 日本語, русский, and émojis 🎉"
        assert result["metadata"]["作者"] == "テスト"


class TestSkillPropertiesDataclass:
    """Tests for SkillProperties dataclass behavior."""

    def test_default_metadata_is_empty_dict(self):
        """Default metadata should be an empty dict, not None."""
        props = SkillProperties(name="my-skill", description="A test skill")

        assert props.metadata == {}
        assert props.metadata is not None

    def test_default_optional_fields_are_none(self):
        """Optional string fields should default to None."""
        props = SkillProperties(name="my-skill", description="A test skill")

        assert props.license is None
        assert props.compatibility is None
        assert props.allowed_tools is None

    def test_instances_have_independent_metadata(self):
        """Each instance should have its own metadata dict (mutable default safety)."""
        props1 = SkillProperties(name="skill-1", description="First")
        props2 = SkillProperties(name="skill-2", description="Second")

        props1.metadata["key"] = "value"

        assert "key" not in props2.metadata
        assert props1.metadata is not props2.metadata

    def test_equality_with_same_values(self):
        """Instances with identical values should be equal."""
        props1 = SkillProperties(
            name="my-skill",
            description="A test skill",
            license="MIT",
        )
        props2 = SkillProperties(
            name="my-skill",
            description="A test skill",
            license="MIT",
        )

        assert props1 == props2

    def test_inequality_with_different_values(self):
        """Instances with different values should not be equal."""
        props1 = SkillProperties(name="skill-a", description="First")
        props2 = SkillProperties(name="skill-b", description="Second")

        assert props1 != props2
