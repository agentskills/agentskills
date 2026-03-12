"""Data models for Agent Skills."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FeatureDefinition:
    """A single feature within a skill.

    Attributes:
        description: Human-readable description of what this feature provides
        section: Markdown heading that starts this feature's content (e.g., "## App Router")
        requires: Other features that must also be activated when this one is active
    """

    description: str
    section: str
    requires: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding empty requires."""
        result = {"description": self.description, "section": self.section}
        if self.requires:
            result["requires"] = self.requires
        return result


@dataclass
class Features:
    """Feature flags for context-aware skill loading.

    Attributes:
        default: Features activated when none are explicitly selected
        available: Map of feature name to feature definition
        conflicts: Sets of mutually exclusive features
    """

    default: list[str]
    available: dict[str, FeatureDefinition]
    conflicts: list[list[str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding empty conflicts."""
        result = {
            "default": self.default,
            "available": {k: v.to_dict() for k, v in self.available.items()},
        }
        if self.conflicts:
            result["conflicts"] = self.conflicts
        return result


@dataclass
class SkillProperties:
    """Properties parsed from a skill's SKILL.md frontmatter.

    Attributes:
        name: Skill name in kebab-case (required)
        description: What the skill does and when the model should use it (required)
        license: License for the skill (optional)
        compatibility: Compatibility information for the skill (optional)
        allowed_tools: Tool patterns the skill requires (optional, experimental)
        features: Feature flags for context-aware loading (optional)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
    """

    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    allowed_tools: Optional[str] = None
    features: Optional[Features] = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {"name": self.name, "description": self.description}
        if self.license is not None:
            result["license"] = self.license
        if self.compatibility is not None:
            result["compatibility"] = self.compatibility
        if self.allowed_tools is not None:
            result["allowed-tools"] = self.allowed_tools
        if self.features is not None:
            result["features"] = self.features.to_dict()
        if self.metadata:
            result["metadata"] = self.metadata
        return result
