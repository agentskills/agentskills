# skills_ref/types/core.py — Core type system for extended AgentSkills

from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any, Literal
from enum import Enum, auto

@dataclass(frozen=True)
class LineColumn:
    line: int    # 1-indexed
    column: int  # 0-indexed
    offset: int  # byte offset from start

@dataclass(frozen=True)
class SourcePosition:
    start: LineColumn
    end: LineColumn

@dataclass
class SkillProperties:
    """Properties parsed from YAML frontmatter."""
    name: str
    description: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    allowed_tools: Optional[List[str]] = None

@dataclass
class ValidationResult:
    """Placeholder for ValidationResult to be defined fully in validation module or here."""
    pass
