"""
Types for skill composition and validation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class DataType(Enum):
    """Supported data types for contracts."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    ANY = "any"


class ErrorHandlingStrategy(Enum):
    """How to handle errors in skill chains."""
    STOP = "stop"          # Stop execution on error
    CONTINUE = "continue"  # Continue with next skill
    COMPENSATE = "compensate"  # Run compensation skills
    RETRY = "retry"        # Retry the failed skill


@dataclass
class FieldSchema:
    """Schema for a contract field."""
    name: str
    type: DataType
    required: bool = True
    description: str = ""
    default: Any = None

    # Array item type
    items_type: Optional[DataType] = None

    # Validation constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    enum_values: Optional[List[Any]] = None

    # Epistemic requirements
    requires_source: bool = False
    requires_rationale: bool = False
    min_items: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "type": self.type.value,
            "required": self.required,
        }
        if self.description:
            result["description"] = self.description
        if self.default is not None:
            result["default"] = self.default
        if self.items_type:
            result["items_type"] = self.items_type.value
        if self.requires_source:
            result["requires_source"] = True
        if self.requires_rationale:
            result["requires_rationale"] = True
        return result


@dataclass
class SkillInputContract:
    """Contract defining expected inputs for a skill."""
    fields: List[FieldSchema] = field(default_factory=list)

    def get_required_fields(self) -> List[FieldSchema]:
        """Get list of required fields."""
        return [f for f in self.fields if f.required]

    def get_optional_fields(self) -> List[FieldSchema]:
        """Get list of optional fields."""
        return [f for f in self.fields if not f.required]

    def get_field(self, name: str) -> Optional[FieldSchema]:
        """Get a field by name."""
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "fields": [f.to_dict() for f in self.fields],
        }


@dataclass
class SkillOutputContract:
    """Contract defining expected outputs from a skill."""
    fields: List[FieldSchema] = field(default_factory=list)

    def get_field(self, name: str) -> Optional[FieldSchema]:
        """Get a field by name."""
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "fields": [f.to_dict() for f in self.fields],
        }


@dataclass
class SkillDefinitionExt:
    """Extended skill definition with contracts."""
    name: str
    description: str = ""
    version: str = "1.0.0"

    # Contracts
    input_contract: SkillInputContract = field(default_factory=SkillInputContract)
    output_contract: SkillOutputContract = field(default_factory=SkillOutputContract)

    # Composition
    level: int = 1  # 1=atomic, 2=composite, 3=workflow
    composes: List[str] = field(default_factory=list)
    operation: str = "READ"  # READ, WRITE, TRANSFORM

    # Execution
    timeout_ms: int = 30000
    retry_count: int = 0

    # Lifecycle
    deprecated_at: Optional[str] = None
    sunset_at: Optional[str] = None


@dataclass
class SkillTransition:
    """A transition between skills in a chain."""
    from_skill: str
    to_skill: str
    condition: Optional[str] = None  # Expression to evaluate
    field_mapping: Dict[str, str] = field(default_factory=dict)  # output -> input mapping

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "from": self.from_skill,
            "to": self.to_skill,
            "condition": self.condition,
            "mapping": self.field_mapping,
        }


@dataclass
class SkillChain:
    """A chain of skills to execute in sequence."""
    id: str
    name: str = ""
    description: str = ""

    # Skills in the chain
    skills: List[SkillDefinitionExt] = field(default_factory=list)

    # Transitions between skills
    transitions: List[SkillTransition] = field(default_factory=list)

    # Error handling
    error_handling: ErrorHandlingStrategy = ErrorHandlingStrategy.STOP
    compensation_skills: List[str] = field(default_factory=list)

    # Execution constraints
    timeout_ms: int = 300000  # 5 min default
    max_retries: int = 0

    def get_skill(self, name: str) -> Optional[SkillDefinitionExt]:
        """Get a skill by name."""
        for s in self.skills:
            if s.name == name:
                return s
        return None

    def get_transition(self, from_skill: str, to_skill: str) -> Optional[SkillTransition]:
        """Get a transition between two skills."""
        for t in self.transitions:
            if t.from_skill == from_skill and t.to_skill == to_skill:
                return t
        return None


class CompositionErrorType(Enum):
    """Types of composition errors."""
    MISSING_SKILL = "missing_skill"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    TYPE_MISMATCH = "type_mismatch"
    MISSING_REQUIRED_INPUT = "missing_required_input"
    INCOMPATIBLE_VERSION = "incompatible_version"
    INVALID_TRANSITION = "invalid_transition"
    LEVEL_VIOLATION = "level_violation"


@dataclass
class CompositionError:
    """An error in skill composition."""
    error_type: CompositionErrorType
    message: str
    skill_name: Optional[str] = None
    field_name: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.error_type.value}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    errors: List[CompositionError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @classmethod
    def success(cls, warnings: Optional[List[str]] = None) -> "ValidationResult":
        """Create successful result."""
        return cls(valid=True, warnings=warnings or [])

    @classmethod
    def failure(cls, errors: List[CompositionError]) -> "ValidationResult":
        """Create failed result."""
        return cls(valid=False, errors=errors)

    def add_error(self, error: CompositionError) -> None:
        """Add an error."""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        self.warnings.append(warning)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge with another result."""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
        )
