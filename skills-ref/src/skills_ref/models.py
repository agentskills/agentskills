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

# Built-in generic types (higher-order skills)
GENERIC_TYPES = {
    "Skill": 2,  # Skill<Input, Output> - skills as first-class values
}


@dataclass
class TypeParam:
    """Type parameter for generic skills.

    Enables skills to be polymorphic, accepting type parameters like:
    - map-skill<A, B>: Skill<A, B> → Skill<A[], B[]>
    - with-retry<A, B>: Skill<A, B> → Skill<A, B>

    Attributes:
        name: Type parameter name (e.g., "A", "B", "T")
        description: Human-readable description
        bound: Optional type bound (e.g., "Skill" for higher-kinded types)
    """
    name: str
    description: Optional[str] = None
    bound: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {"name": self.name}
        if self.description:
            result["description"] = self.description
        if self.bound:
            result["bound"] = self.bound
        return result


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


class LessonStatus(Enum):
    """Lifecycle status for a lesson.

    Lessons progress through stages as they accumulate evidence:
    - OBSERVED: Pattern noticed from single execution
    - PROPOSED: Suggested improvement, awaiting validation
    - VALIDATED: Confirmed across multiple executions
    - APPLIED: Lesson has been crystallised into skill definition
    - DEPRECATED: No longer applicable (context changed)
    """
    OBSERVED = "observed"
    PROPOSED = "proposed"
    VALIDATED = "validated"
    APPLIED = "applied"
    DEPRECATED = "deprecated"


@dataclass
class Lesson:
    """A lesson learned from skill execution.

    Lessons capture patterns discovered during execution that could improve
    the skill definition. They follow the EnvZero-inspired schema:

    - **context**: WHEN this lesson applies (trigger condition)
    - **learned**: WHAT to do differently (the insight)
    - **proposed_edit**: HOW to change the skill (optional diff suggestion)

    Benefits of structured lessons:
    1. **Institutional Memory**: Knowledge persists across sessions
    2. **Continuous Improvement**: Skills evolve from real usage
    3. **Human-in-the-Loop**: Changes require approval before applying
    4. **Confidence Tracking**: Only high-confidence lessons get proposed

    Attributes:
        id: Unique identifier (L-SKILL-NNN format)
        context: When this lesson applies (trigger condition)
        learned: The insight or pattern discovered
        confidence: Confidence score 0.0-1.0 (validated lessons > 0.8)
        source: Where the lesson was discovered (execution_id, feedback, etc.)
        status: Lifecycle stage (observed → proposed → validated → applied)
        proposed_edit: Optional suggested change to the skill definition
        validated_at: ISO date when lesson reached validated status
        applied_at: ISO date when lesson was crystallised into skill
    """
    id: str
    context: str
    learned: str
    confidence: float = 0.5
    source: Optional[str] = None
    status: str = "observed"
    proposed_edit: Optional[str] = None
    validated_at: Optional[str] = None
    applied_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {
            "id": self.id,
            "context": self.context,
            "learned": self.learned,
            "confidence": self.confidence,
            "status": self.status,
        }
        if self.source:
            result["source"] = self.source
        if self.proposed_edit:
            result["proposed_edit"] = self.proposed_edit
        if self.validated_at:
            result["validated_at"] = self.validated_at
        if self.applied_at:
            result["applied_at"] = self.applied_at
        return result

    @property
    def is_actionable(self) -> bool:
        """Check if lesson has enough confidence to propose changes."""
        return self.confidence >= 0.8 and self.status in ("proposed", "validated")

    @property
    def ready_to_apply(self) -> bool:
        """Check if lesson is validated and has a proposed edit."""
        return (
            self.status == "validated"
            and self.confidence >= 0.9
            and self.proposed_edit is not None
        )


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
        type_params: Type parameters for generic/higher-order skills (optional)
        inputs: Input field schemas for type checking (optional)
        outputs: Output field schemas for type checking (optional)
        lessons: Lessons learned from execution (optional, for continuous improvement)
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
    # Type checking fields (including generics)
    type_params: Optional[list[TypeParam]] = None
    inputs: Optional[list[FieldSchema]] = None
    outputs: Optional[list[FieldSchema]] = None
    # Continuous improvement fields
    lessons: Optional[list[Lesson]] = None

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
        # Type checking fields (including generics)
        if self.type_params:
            result["type_params"] = [tp.to_dict() for tp in self.type_params]
        if self.inputs:
            result["inputs"] = [f.to_dict() for f in self.inputs]
        if self.outputs:
            result["outputs"] = [f.to_dict() for f in self.outputs]
        # Continuous improvement fields
        if self.lessons:
            result["lessons"] = [lesson.to_dict() for lesson in self.lessons]
        return result

    @property
    def is_generic(self) -> bool:
        """Check if this skill has type parameters (is a higher-order skill)."""
        return bool(self.type_params)

    @property
    def type_param_names(self) -> set[str]:
        """Get the set of type parameter names for this skill."""
        if not self.type_params:
            return set()
        return {tp.name for tp in self.type_params}

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

    # =========================================================================
    # Lesson-related properties (continuous improvement)
    # =========================================================================

    @property
    def has_lessons(self) -> bool:
        """Check if this skill has accumulated lessons."""
        return bool(self.lessons)

    @property
    def actionable_lessons(self) -> list[Lesson]:
        """Get lessons with high enough confidence to propose changes.

        Returns lessons where confidence >= 0.8 and status is proposed/validated.
        These are candidates for the skill-evolver to generate edits.
        """
        if not self.lessons:
            return []
        return [l for l in self.lessons if l.is_actionable]

    @property
    def lessons_ready_to_apply(self) -> list[Lesson]:
        """Get lessons that are validated and ready for human approval.

        Returns lessons where:
        - status is 'validated'
        - confidence >= 0.9
        - proposed_edit is not None

        These lessons have been tested multiple times and have concrete
        edit suggestions ready for human review.
        """
        if not self.lessons:
            return []
        return [l for l in self.lessons if l.ready_to_apply]

    @property
    def lesson_stats(self) -> dict[str, int]:
        """Get counts of lessons by status.

        Returns:
            Dict with counts: {observed: N, proposed: N, validated: N, applied: N}
        """
        if not self.lessons:
            return {}
        stats: dict[str, int] = {}
        for lesson in self.lessons:
            stats[lesson.status] = stats.get(lesson.status, 0) + 1
        return stats
