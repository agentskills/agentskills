"""Tests for errors module."""

import pytest

from skills_ref.errors import ParseError, SkillError, ValidationError


class TestSkillError:
    """Tests for SkillError base exception."""

    def test_skill_error_is_exception(self):
        """SkillError should be a subclass of Exception."""
        assert issubclass(SkillError, Exception)

    def test_skill_error_can_be_raised(self):
        """SkillError should be raisable with a message."""
        with pytest.raises(SkillError, match="test message"):
            raise SkillError("test message")

    def test_skill_error_message_accessible(self):
        """SkillError message should be accessible via args."""
        error = SkillError("my error message")
        assert str(error) == "my error message"
        assert error.args[0] == "my error message"


class TestParseError:
    """Tests for ParseError exception."""

    def test_parse_error_inherits_skill_error(self):
        """ParseError should be a subclass of SkillError."""
        assert issubclass(ParseError, SkillError)

    def test_parse_error_can_be_raised(self):
        """ParseError should be raisable with a message."""
        with pytest.raises(ParseError, match="invalid YAML"):
            raise ParseError("invalid YAML")

    def test_parse_error_caught_as_skill_error(self):
        """ParseError should be catchable as SkillError."""
        with pytest.raises(SkillError):
            raise ParseError("parsing failed")


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_inherits_skill_error(self):
        """ValidationError should be a subclass of SkillError."""
        assert issubclass(ValidationError, SkillError)

    def test_validation_error_single_message(self):
        """ValidationError with single message populates errors list."""
        error = ValidationError("field is required")

        assert str(error) == "field is required"
        assert error.errors == ["field is required"]

    def test_validation_error_with_errors_list(self):
        """ValidationError can accept explicit errors list."""
        errors_list = ["error 1", "error 2", "error 3"]
        error = ValidationError("multiple errors", errors=errors_list)

        assert str(error) == "multiple errors"
        assert error.errors == errors_list
        assert len(error.errors) == 3

    def test_validation_error_errors_attribute_accessible(self):
        """ValidationError.errors attribute should be accessible."""
        error = ValidationError("test", errors=["a", "b"])

        assert hasattr(error, "errors")
        assert isinstance(error.errors, list)

    def test_validation_error_empty_errors_list(self):
        """ValidationError with empty errors list should work."""
        error = ValidationError("no details", errors=[])

        assert error.errors == []

    def test_validation_error_caught_as_skill_error(self):
        """ValidationError should be catchable as SkillError."""
        with pytest.raises(SkillError):
            raise ValidationError("validation failed")
