"""
Skill Composition & Safety for AgentSkills Enterprise.

This module provides:
- Input/output contract validation
- Skill chain validation
- Composition graph analysis
- Version compatibility checking
"""

from .types import (
    DataType,
    ErrorHandlingStrategy,
    OperationType,
    ResourceConstraints,
    FieldSchema,
    SkillInputContract,
    SkillOutputContract,
    SkillDefinitionExt,
    SkillChain,
    SkillTransition,
    CompositionError,
    CompositionErrorType,
    ValidationResult,
)
from .validator import (
    ContractValidator,
    CompositionValidator,
)
from .executor import SkillChainExecutor, SkillExecutionResult, ChainExecutionResult

__all__ = [
    # Enums
    "DataType",
    "ErrorHandlingStrategy",
    "OperationType",
    "CompositionErrorType",
    # Types
    "ResourceConstraints",
    "FieldSchema",
    "SkillInputContract",
    "SkillOutputContract",
    "SkillDefinitionExt",
    "SkillChain",
    "SkillTransition",
    "CompositionError",
    "ValidationResult",
    # Validators
    "ContractValidator",
    "CompositionValidator",
    # Executor
    "SkillChainExecutor",
    "SkillExecutionResult",
    "ChainExecutionResult",
]
