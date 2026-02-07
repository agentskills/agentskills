"""Reference library for Agent Skills."""

from .errors import ParseError, SkillError, ValidationError
from .models import SkillProperties
from .parser import find_skill_md, read_properties
from .prompt import to_prompt
from .validator import validate
from .management import create_skill, edit_skill, delete_skill, list_skills

__all__ = [
    "SkillError",
    "ParseError",
    "ValidationError",
    "SkillProperties",
    "find_skill_md",
    "validate",
    "read_properties",
    "to_prompt",
    "create_skill",
    "edit_skill",
    "delete_skill",
    "list_skills"
]

__version__ = "0.1.0"
