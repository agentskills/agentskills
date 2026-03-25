"""Data models for Agent Skills."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SkillProperties:
    """Properties parsed from a skill's SKILL.md frontmatter.

    Attributes:
        name: Skill name in kebab-case (required)
        description: What the skill does and when the model should use it (required)
        argument_hint: Hint for arguments the skill accepts (optional, Claude Code)
        compatibility: Compatibility information for the skill (optional)
        disable_model_invocation: Prevent programmatic invocation (optional, Claude Code)
        license: License for the skill (optional)
        model: Model override for the skill (optional, Claude Code)
        allowed_tools: Tool patterns the skill requires (optional, experimental)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
    """

    name: str
    description: str
    argument_hint: Optional[str] = None
    compatibility: Optional[str] = None
    disable_model_invocation: Optional[bool] = None
    license: Optional[str] = None
    model: Optional[str] = None
    allowed_tools: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {"name": self.name, "description": self.description}
        if self.argument_hint is not None:
            result["argument-hint"] = self.argument_hint
        if self.compatibility is not None:
            result["compatibility"] = self.compatibility
        if self.disable_model_invocation is not None:
            result["disable-model-invocation"] = self.disable_model_invocation
        if self.license is not None:
            result["license"] = self.license
        if self.model is not None:
            result["model"] = self.model
        if self.allowed_tools is not None:
            result["allowed-tools"] = self.allowed_tools
        if self.metadata:
            result["metadata"] = self.metadata
        return result
