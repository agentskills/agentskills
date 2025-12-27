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


# =============================================================================
# Versioning System
# =============================================================================


class ChangeType(Enum):
    """Classification of changes for semantic versioning.

    Used to determine version bump type:
    - BREAKING: Requires MAJOR version bump (removes outputs, changes required inputs)
    - FEATURE: Requires MINOR version bump (adds optional outputs/inputs)
    - FIX: Requires PATCH version bump (bug fixes, doc updates)
    """
    BREAKING = "breaking"
    FEATURE = "feature"
    FIX = "fix"


@dataclass
class VersionChange:
    """A single change in a version's changelog.

    Attributes:
        change_type: Classification (breaking, feature, fix)
        description: Human-readable description of the change
        lesson_id: Optional link to the lesson that triggered this change
        migration: Optional migration guidance for breaking changes
    """
    change_type: str
    description: str
    lesson_id: Optional[str] = None
    migration: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {
            "change_type": self.change_type,
            "description": self.description,
        }
        if self.lesson_id:
            result["lesson_id"] = self.lesson_id
        if self.migration:
            result["migration"] = self.migration
        return result


@dataclass
class VersionEntry:
    """A version in the skill's version history.

    Follows semantic versioning (MAJOR.MINOR.PATCH):
    - MAJOR: Breaking changes (consumers must update)
    - MINOR: Backwards-compatible additions
    - PATCH: Bug fixes and documentation

    Attributes:
        version: Semantic version string (e.g., "1.2.0")
        released_at: ISO date when this version was released
        changes: List of changes in this version
        deprecated: Whether this version is deprecated
        sunset_date: ISO date when this version will be removed (if deprecated)
    """
    version: str
    released_at: str
    changes: list[VersionChange] = field(default_factory=list)
    deprecated: bool = False
    sunset_date: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None/default values."""
        result = {
            "version": self.version,
            "released_at": self.released_at,
        }
        if self.changes:
            result["changes"] = [c.to_dict() for c in self.changes]
        if self.deprecated:
            result["deprecated"] = True
        if self.sunset_date:
            result["sunset_date"] = self.sunset_date
        return result

    @property
    def major(self) -> int:
        """Extract major version number."""
        parts = self.version.split(".")
        return int(parts[0]) if parts else 0

    @property
    def minor(self) -> int:
        """Extract minor version number."""
        parts = self.version.split(".")
        return int(parts[1]) if len(parts) > 1 else 0

    @property
    def patch(self) -> int:
        """Extract patch version number."""
        parts = self.version.split(".")
        return int(parts[2]) if len(parts) > 2 else 0

    @property
    def has_breaking_changes(self) -> bool:
        """Check if this version contains breaking changes."""
        return any(c.change_type == ChangeType.BREAKING.value for c in self.changes)


@dataclass
class VersionConstraint:
    """A constraint on skill version compatibility.

    Used by consuming skills to declare version requirements.

    Attributes:
        skill_name: Name of the required skill
        constraint: Version constraint (e.g., ">=1.0.0", "^2.0", "~1.2")
    """
    skill_name: str
    constraint: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "skill_name": self.skill_name,
            "constraint": self.constraint,
        }

    def satisfies(self, version: str) -> bool:
        """Check if a version satisfies this constraint.

        Supports:
        - Exact: "1.2.3" (must match exactly)
        - Greater/equal: ">=1.2.0" (must be at least this version)
        - Caret: "^1.2.0" (compatible with 1.x.x, x >= 2)
        - Tilde: "~1.2.0" (compatible with 1.2.x)

        Args:
            version: Version string to check

        Returns:
            True if version satisfies the constraint
        """
        # Parse version into components
        def parse_version(v: str) -> tuple[int, int, int]:
            parts = v.replace(">=", "").replace("^", "").replace("~", "").split(".")
            major = int(parts[0]) if parts else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)

        actual = parse_version(version)
        required = parse_version(self.constraint)

        # Exact match
        if not any(c in self.constraint for c in [">=", "^", "~"]):
            return actual == required

        # Greater/equal
        if self.constraint.startswith(">="):
            return actual >= required

        # Caret: compatible within major version
        if self.constraint.startswith("^"):
            if actual[0] != required[0]:
                return False
            if actual[0] == 0:
                # 0.x.y: minor version must match
                return actual[1] == required[1] and actual[2] >= required[2]
            return actual >= required

        # Tilde: compatible within minor version
        if self.constraint.startswith("~"):
            return actual[0] == required[0] and actual[1] == required[1] and actual[2] >= required[2]

        return False


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


# =============================================================================
# Optional Formalism System (Semantic Foundations)
# =============================================================================


class FormalismLevel(Enum):
    """Optional formalism level for skills.

    Skills can opt into increasing levels of formal specification:
    - BASIC: Default - name, description, optional composability
    - TYPED: Adds typed inputs/outputs for static checking
    - EFFECTS: Adds effect declarations (finer than READ/WRITE)
    - FORMAL: Full string-diagrammatic wiring with ports

    Each level is backwards-compatible: a FORMAL skill validates
    at all lower levels too.
    """
    BASIC = "basic"      # No type requirements
    TYPED = "typed"      # Requires inputs/outputs schemas
    EFFECTS = "effects"  # Requires effect declarations
    FORMAL = "formal"    # Requires explicit wiring


# Supported algebraic effects (optional, finer-grained than operation)
EFFECT_TYPES = {
    "Query",      # Pure read from external source
    "Mutate",     # State modification
    "Fail",       # May fail/error
    "Timeout",    # Time-bounded operation
    "Memo",       # Memoizable/cacheable
    "Log",        # Produces log output
    "Network",    # Network access
    "FileRead",   # File system read
    "FileWrite",  # File system write
}


@dataclass
class EffectDeclaration:
    """Declaration of an algebraic effect a skill may raise.

    Effects provide finer-grained classification than operation:
    - A READ skill might raise {Query, Fail, Network}
    - A WRITE skill might raise {Mutate, Fail, Log}

    Benefits of explicit effects:
    1. **Effect inference**: Composite effects = union of child effects
    2. **Handler matching**: Decorators can target specific effects
    3. **Safety proofs**: Prove workflows handle all raised effects

    Attributes:
        name: Effect type name (from EFFECT_TYPES)
        description: Optional context for this effect
        handled_by: Optional skill that handles this effect
    """
    name: str
    description: Optional[str] = None
    handled_by: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {"name": self.name}
        if self.description:
            result["description"] = self.description
        if self.handled_by:
            result["handled_by"] = self.handled_by
        return result


@dataclass
class Port:
    """A named port for string-diagrammatic wiring.

    Ports make data flow explicit in compositions. Instead of
    implicit matching by field name, ports declare exactly how
    skills connect.

    Attributes:
        name: Port name (unique within skill)
        type: Type of data flowing through port
        direction: "in" or "out"
        field: Optional mapping to input/output field
    """
    name: str
    type: str
    direction: str  # "in" or "out"
    field: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {
            "name": self.name,
            "type": self.type,
            "direction": self.direction,
        }
        if self.field:
            result["field"] = self.field
        return result


@dataclass
class Wire:
    """A connection between ports in a composition.

    Wires make the data flow graph explicit, enabling:
    - Visual rendering as string diagrams
    - Static type checking of connections
    - Deterministic execution order

    Attributes:
        from_skill: Source skill name (or "input" for workflow input)
        from_port: Source port name
        to_skill: Target skill name (or "output" for workflow output)
        to_port: Target port name
    """
    from_skill: str
    from_port: str
    to_skill: str
    to_port: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "from_skill": self.from_skill,
            "from_port": self.from_port,
            "to_skill": self.to_skill,
            "to_port": self.to_port,
        }


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
        version: Current semantic version (e.g., "1.2.0")
        version_history: List of past versions with changelogs
        requires: Version constraints for composed skills
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
    # Versioning fields
    version: Optional[str] = None
    version_history: Optional[list[VersionEntry]] = None
    requires: Optional[list[VersionConstraint]] = None
    # Optional formalism fields (semantic foundations)
    formalism: Optional[str] = None  # FormalismLevel value
    effects: Optional[list[EffectDeclaration]] = None
    ports: Optional[list[Port]] = None
    wiring: Optional[list[Wire]] = None

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
        # Versioning fields
        if self.version:
            result["version"] = self.version
        if self.version_history:
            result["version_history"] = [v.to_dict() for v in self.version_history]
        if self.requires:
            result["requires"] = [r.to_dict() for r in self.requires]
        # Optional formalism fields
        if self.formalism:
            result["formalism"] = self.formalism
        if self.effects:
            result["effects"] = [e.to_dict() for e in self.effects]
        if self.ports:
            result["ports"] = [p.to_dict() for p in self.ports]
        if self.wiring:
            result["wiring"] = [w.to_dict() for w in self.wiring]
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

    # =========================================================================
    # Version-related properties
    # =========================================================================

    @property
    def is_versioned(self) -> bool:
        """Check if this skill has explicit versioning."""
        return self.version is not None

    @property
    def current_version(self) -> Optional[VersionEntry]:
        """Get the current version entry from history.

        Returns the version_history entry matching the current version,
        or None if no match or no history.
        """
        if not self.version or not self.version_history:
            return None
        for entry in self.version_history:
            if entry.version == self.version:
                return entry
        return None

    @property
    def is_deprecated(self) -> bool:
        """Check if the current version is deprecated."""
        current = self.current_version
        return current.deprecated if current else False

    @property
    def latest_version(self) -> Optional[VersionEntry]:
        """Get the latest version entry from history.

        Returns the version with the highest semver number.
        """
        if not self.version_history:
            return None
        return max(
            self.version_history,
            key=lambda v: (v.major, v.minor, v.patch)
        )

    @property
    def breaking_changes_since(self) -> list[VersionEntry]:
        """Get all versions with breaking changes.

        Useful for migration planning - shows all versions
        that require consumer updates.
        """
        if not self.version_history:
            return []
        return [v for v in self.version_history if v.has_breaking_changes]

    def version_satisfies(self, constraint: VersionConstraint) -> bool:
        """Check if current version satisfies a constraint.

        Args:
            constraint: Version constraint to check

        Returns:
            True if current version satisfies the constraint
        """
        if not self.version:
            return False
        return constraint.satisfies(self.version)

    def check_requires(self, available_skills: dict[str, "SkillProperties"]) -> list[str]:
        """Check if all version requirements are satisfied.

        Args:
            available_skills: Dict mapping skill names to their properties

        Returns:
            List of error messages for unsatisfied requirements
        """
        errors = []
        if not self.requires:
            return errors

        for req in self.requires:
            if req.skill_name not in available_skills:
                errors.append(
                    f"Required skill '{req.skill_name}' not found"
                )
                continue

            skill = available_skills[req.skill_name]
            if not skill.version:
                errors.append(
                    f"Skill '{req.skill_name}' has no version, "
                    f"but '{self.name}' requires {req.constraint}"
                )
                continue

            if not req.satisfies(skill.version):
                errors.append(
                    f"Skill '{req.skill_name}' version {skill.version} "
                    f"does not satisfy requirement {req.constraint}"
                )

        return errors

    # =========================================================================
    # Formalism-related properties (optional semantic foundations)
    # =========================================================================

    @property
    def declared_formalism(self) -> str:
        """Get the declared formalism level, defaulting to 'basic'."""
        return self.formalism or FormalismLevel.BASIC.value

    @property
    def inferred_formalism(self) -> str:
        """Infer the minimum formalism level from present fields.

        Returns the highest level implied by the fields present:
        - FORMAL if wiring is present
        - EFFECTS if effects are present
        - TYPED if inputs/outputs are present
        - BASIC otherwise
        """
        if self.wiring:
            return FormalismLevel.FORMAL.value
        if self.effects:
            return FormalismLevel.EFFECTS.value
        if self.inputs or self.outputs:
            return FormalismLevel.TYPED.value
        return FormalismLevel.BASIC.value

    @property
    def has_effects(self) -> bool:
        """Check if this skill has effect declarations."""
        return bool(self.effects)

    @property
    def effect_names(self) -> set[str]:
        """Get the set of effect names raised by this skill."""
        if not self.effects:
            return set()
        return {e.name for e in self.effects}

    @property
    def has_wiring(self) -> bool:
        """Check if this skill has explicit wiring (string diagram)."""
        return bool(self.wiring)

    @property
    def has_ports(self) -> bool:
        """Check if this skill has port declarations."""
        return bool(self.ports)

    def infer_effects_from_operation(self) -> set[str]:
        """Infer effects from the operation field if no explicit effects.

        Provides a bridge from basic operation classification to effects:
        - READ → {Query}
        - WRITE → {Mutate, Fail}
        - TRANSFORM → {} (pure)

        Returns:
            Set of inferred effect names
        """
        if self.effects:
            return self.effect_names

        if self.operation == SkillOperation.READ.value:
            return {"Query"}
        if self.operation == SkillOperation.WRITE.value:
            return {"Mutate", "Fail"}
        if self.operation == SkillOperation.TRANSFORM.value:
            return set()
        return set()
