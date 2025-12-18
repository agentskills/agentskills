"""Reference library for Agent Skills."""

from .errors import ParseError, SkillError, ValidationError
from .graph import CompositionGraph, GraphAnalysis, SkillNode, validate_composition
from .models import SkillLevel, SkillOperation, SkillProperties
from .parser import find_skill_md, read_properties
from .prompt import to_prompt
from .validator import validate

__all__ = [
    # Errors
    "SkillError",
    "ParseError",
    "ValidationError",
    # Models
    "SkillProperties",
    "SkillLevel",
    "SkillOperation",
    # Graph (composability)
    "CompositionGraph",
    "GraphAnalysis",
    "SkillNode",
    "validate_composition",
    # Parser
    "find_skill_md",
    "read_properties",
    # Validator
    "validate",
    # Prompt generation
    "to_prompt",
]

__version__ = "0.1.0"
