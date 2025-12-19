"""Data models for Agent Skills."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


# =============================================================================
# Type System for Skill Inputs/Outputs
# =============================================================================

# Built-in primitive types
PRIMITIVE_TYPES = {
    "string", "number", "integer", "boolean", "date", "datetime", "any"
}


@dataclass
class FieldSchema:
    """Schema for an input or output field.

    Attributes:
        name: Field name
        type: Type name (primitive or custom)
        required: Whether field is required (default True for inputs)
        description: Human-readable description
        default: Default value if not provided
        requires_source: Output must cite a source (prevents hallucination)
        requires_rationale: Output must include reasoning
        min_length: Minimum string length (for rationale)
        min_items: Minimum list items (for sources)
        range: Valid range for numbers [min, max]
    """
    name: str
    type: str
    required: bool = True
    description: Optional[str] = None
    default: Any = None
    # Epistemic requirements (prevent hallucination)
    requires_source: bool = False
    requires_rationale: bool = False
    min_length: Optional[int] = None
    min_items: Optional[int] = None
    range: Optional[tuple[float, float]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None/False values."""
        result = {"name": self.name, "type": self.type}
        if not self.required:
            result["required"] = False
        if self.description:
            result["description"] = self.description
        if self.default is not None:
            result["default"] = self.default
        if self.requires_source:
            result["requires_source"] = True
        if self.requires_rationale:
            result["requires_rationale"] = True
        if self.min_length is not None:
            result["min_length"] = self.min_length
        if self.min_items is not None:
            result["min_items"] = self.min_items
        if self.range is not None:
            result["range"] = list(self.range)
        return result


@dataclass
class TypeDefinition:
    """Custom type definition.

    Attributes:
        name: Type name (e.g., "DateRange", "Citation")
        fields: Dictionary of field name to type string
        description: Human-readable description
    """
    name: str
    fields: dict[str, str]
    description: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {"name": self.name, "fields": self.fields}
        if self.description:
            result["description"] = self.description
        return result


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
        inputs: Input field schemas for type checking (optional)
        outputs: Output field schemas for type checking (optional)
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
    # Type checking fields
    inputs: Optional[list[FieldSchema]] = None
    outputs: Optional[list[FieldSchema]] = None

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
        # Type checking fields
        if self.inputs:
            result["inputs"] = [f.to_dict() for f in self.inputs]
        if self.outputs:
            result["outputs"] = [f.to_dict() for f in self.outputs]
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
