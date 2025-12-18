"""Skill-related exceptions."""


class SkillError(Exception):
    """Base exception for all skill-related errors."""

    pass


class ParseError(SkillError):
    """Raised when SKILL.md parsing fails."""

    pass


class ValidationError(SkillError):
    """Raised when skill properties are invalid.

    Attributes:
        errors: List of validation error messages (may contain just one)
    """

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors if errors is not None else [message]
