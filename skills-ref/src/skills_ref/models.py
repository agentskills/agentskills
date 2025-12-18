"""Data models for Agent Skills."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SkillLevel(Enum):
    """Composition hierarchy level for a skill.

    Skills can be organised into levels like higher-order functions:
    - Level 1 (Atomic): Single-purpose operations (READ or WRITE one thing)
    - Level 2 (Composite): Combines multiple atomic skills
    - Level 3 (Workflow): Complex orchestration with decision logic
    """
    ATOMIC = 1
    COMPOSITE = 2
    WORKFLOW = 3


class SkillOperation(Enum):
    """Safety classification for a skill.

    Determines whether user confirmation is recommended:
    - READ: Only reads data, no side effects (safe)
    - WRITE: Creates, modifies, or deletes data (needs confirmation)
    - TRANSFORM: Local-only transformation (safe)
    """
    READ = "READ"
    WRITE = "WRITE"
    TRANSFORM = "TRANSFORM"


@dataclass
class SkillProperties:
    """Properties parsed from a skill's SKILL.md frontmatter.

    Attributes:
        name: Skill name in kebab-case (required)
        description: What the skill does and when the model should use it (required)
        license: License for the skill (optional)
        compatibility: Compatibility information for the skill (optional)
        allowed_tools: Tool patterns the skill requires (optional, experimental)
        metadata: Key-value pairs for client-specific properties (defaults to
            empty dict; omitted from to_dict() output when empty)
        level: Composition hierarchy level 1-3 (optional, for composable skills)
        operation: Safety classification READ/WRITE/TRANSFORM (optional)
        composes: List of skill names this skill depends on (optional)
    """

    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    allowed_tools: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)
    # Composability fields
    level: Optional[int] = None
    operation: Optional[str] = None
    composes: Optional[list[str]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {"name": self.name, "description": self.description}
        if self.license is not None:
            result["license"] = self.license
        if self.compatibility is not None:
            result["compatibility"] = self.compatibility
        if self.allowed_tools is not None:
            result["allowed-tools"] = self.allowed_tools
        if self.metadata:
            result["metadata"] = self.metadata
        # Composability fields
        if self.level is not None:
            result["level"] = self.level
        if self.operation is not None:
            result["operation"] = self.operation
        if self.composes:
            result["composes"] = self.composes
        return result

    @property
    def is_atomic(self) -> bool:
        """Check if this is a Level 1 atomic skill."""
        return self.level == SkillLevel.ATOMIC.value

    @property
    def is_composite(self) -> bool:
        """Check if this is a Level 2 composite skill."""
        return self.level == SkillLevel.COMPOSITE.value

    @property
    def is_workflow(self) -> bool:
        """Check if this is a Level 3 workflow skill."""
        return self.level == SkillLevel.WORKFLOW.value

    @property
    def is_read_only(self) -> bool:
        """Check if this skill only reads data (safe to run without confirmation)."""
        return self.operation in (SkillOperation.READ.value, SkillOperation.TRANSFORM.value)

    @property
    def needs_confirmation(self) -> bool:
        """Check if this skill should require user confirmation."""
        return self.operation == SkillOperation.WRITE.value
