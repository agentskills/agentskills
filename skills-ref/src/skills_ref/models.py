"""Data models for Agent Skills."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Credential:
    """A credential declared by a skill.

    Attributes:
        name: Environment-variable-style identifier (e.g. OPENAI_API_KEY)
        description: What the credential is for
        required: Whether the skill requires this credential (defaults to True)
    """

    name: str
    description: str
    required: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {"name": self.name, "description": self.description}
        if not self.required:
            result["required"] = False
        return result


@dataclass
class SkillProperties:
    """Properties parsed from a skill's SKILL.md frontmatter.

    Attributes:
        name: Skill name in kebab-case (required)
        description: What the skill does and when the model should use it (required)
        license: License for the skill (optional)
        compatibility: Compatibility information for the skill (optional)
        credentials: List of credentials the skill requires (optional)
        allowed_tools: Tool patterns the skill requires (optional, experimental)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
    """

    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    credentials: Optional[list[Credential]] = None
    allowed_tools: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {"name": self.name, "description": self.description}
        if self.license is not None:
            result["license"] = self.license
        if self.compatibility is not None:
            result["compatibility"] = self.compatibility
        if self.credentials is not None:
            result["credentials"] = [c.to_dict() for c in self.credentials]
        if self.allowed_tools is not None:
            result["allowed-tools"] = self.allowed_tools
        if self.metadata:
            result["metadata"] = self.metadata
        return result
