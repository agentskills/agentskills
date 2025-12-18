"""Skill validation logic."""

import unicodedata
from pathlib import Path
from typing import Optional

from .errors import ParseError
from .parser import find_skill_md, parse_frontmatter

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500

# Allowed frontmatter fields per Agent Skills Spec
ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
    # Composability fields
    "level",
    "operation",
    "composes",
}

# Valid values for composability fields
VALID_LEVELS = {1, 2, 3}
VALID_OPERATIONS = {"READ", "WRITE", "TRANSFORM"}


def _validate_name(name: str, skill_dir: Path) -> list[str]:
    """Validate skill name format and directory match.

    Skill names support i18n characters (Unicode letters) plus hyphens.
    Names must be lowercase and cannot start/end with hyphens.
    """
    errors = []

    if not name or not isinstance(name, str) or not name.strip():
        errors.append("Field 'name' must be a non-empty string")
        return errors

    name = unicodedata.normalize("NFKC", name.strip())

    if len(name) > MAX_SKILL_NAME_LENGTH:
        errors.append(
            f"Skill name '{name}' exceeds {MAX_SKILL_NAME_LENGTH} character limit "
            f"({len(name)} chars)"
        )

    if name != name.lower():
        errors.append(f"Skill name '{name}' must be lowercase")

    if name.startswith("-") or name.endswith("-"):
        errors.append("Skill name cannot start or end with a hyphen")

    if "--" in name:
        errors.append("Skill name cannot contain consecutive hyphens")

    if not all(c.isalnum() or c == "-" for c in name):
        errors.append(
            f"Skill name '{name}' contains invalid characters. "
            "Only letters, digits, and hyphens are allowed."
        )

    if skill_dir:
        dir_name = unicodedata.normalize("NFKC", skill_dir.name)
        if dir_name != name:
            errors.append(
                f"Directory name '{skill_dir.name}' must match skill name '{name}'"
            )

    return errors


def _validate_description(description: str) -> list[str]:
    """Validate description format."""
    errors = []

    if not description or not isinstance(description, str) or not description.strip():
        errors.append("Field 'description' must be a non-empty string")
        return errors

    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"Description exceeds {MAX_DESCRIPTION_LENGTH} character limit "
            f"({len(description)} chars)"
        )

    return errors


def _validate_compatibility(compatibility: str) -> list[str]:
    """Validate compatibility format."""
    errors = []

    if not isinstance(compatibility, str):
        errors.append("Field 'compatibility' must be a string")
        return errors

    if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
        errors.append(
            f"Compatibility exceeds {MAX_COMPATIBILITY_LENGTH} character limit "
            f"({len(compatibility)} chars)"
        )

    return errors


def _validate_metadata_fields(metadata: dict) -> list[str]:
    """Validate that only allowed fields are present."""
    errors = []

    extra_fields = set(metadata.keys()) - ALLOWED_FIELDS
    if extra_fields:
        errors.append(
            f"Unexpected fields in frontmatter: {', '.join(sorted(extra_fields))}. "
            f"Only {sorted(ALLOWED_FIELDS)} are allowed."
        )

    return errors


def _validate_level(level) -> list[str]:
    """Validate the level field for composability.

    Level indicates where a skill sits in the composition hierarchy:
    - 1 (Atomic): Single-purpose operations
    - 2 (Composite): Combines multiple atomic skills
    - 3 (Workflow): Complex orchestration with decision logic
    """
    errors = []

    if not isinstance(level, int):
        errors.append(f"Field 'level' must be an integer, got {type(level).__name__}")
        return errors

    if level not in VALID_LEVELS:
        errors.append(
            f"Field 'level' must be 1, 2, or 3 (got {level}). "
            "1=Atomic, 2=Composite, 3=Workflow"
        )

    return errors


def _validate_operation(operation) -> list[str]:
    """Validate the operation field for safety classification.

    Operation classifies a skill's safety level:
    - READ: Only reads data, no side effects (safe)
    - WRITE: Creates, modifies, or deletes data (needs confirmation)
    - TRANSFORM: Local-only transformation (safe)
    """
    errors = []

    if not isinstance(operation, str):
        errors.append(f"Field 'operation' must be a string, got {type(operation).__name__}")
        return errors

    if operation not in VALID_OPERATIONS:
        errors.append(
            f"Field 'operation' must be one of {sorted(VALID_OPERATIONS)}, got '{operation}'"
        )

    return errors


def _validate_composes(composes, level=None) -> list[str]:
    """Validate the composes field for skill dependencies.

    Composes lists the skills this skill depends on.
    """
    errors = []

    if not isinstance(composes, list):
        errors.append(f"Field 'composes' must be a list, got {type(composes).__name__}")
        return errors

    for i, skill_name in enumerate(composes):
        if not isinstance(skill_name, str):
            errors.append(f"Field 'composes[{i}]' must be a string, got {type(skill_name).__name__}")
        elif not skill_name.strip():
            errors.append(f"Field 'composes[{i}]' cannot be empty")

    # Warn if level 1 has composes (atomic skills shouldn't compose)
    if level == 1 and composes:
        errors.append(
            "Level 1 (Atomic) skills should not have 'composes'. "
            "Atomic skills wrap primitives, not other skills."
        )

    return errors


def validate_metadata(metadata: dict, skill_dir: Optional[Path] = None) -> list[str]:
    """Validate parsed skill metadata.

    This is the core validation function that works on already-parsed metadata,
    avoiding duplicate file I/O when called from the parser.

    Args:
        metadata: Parsed YAML frontmatter dictionary
        skill_dir: Optional path to skill directory (for name-directory match check)

    Returns:
        List of validation error messages. Empty list means valid.
    """
    errors = []
    errors.extend(_validate_metadata_fields(metadata))

    if "name" not in metadata:
        errors.append("Missing required field in frontmatter: name")
    else:
        errors.extend(_validate_name(metadata["name"], skill_dir))

    if "description" not in metadata:
        errors.append("Missing required field in frontmatter: description")
    else:
        errors.extend(_validate_description(metadata["description"]))

    if "compatibility" in metadata:
        errors.extend(_validate_compatibility(metadata["compatibility"]))

    # Validate composability fields
    level = metadata.get("level")
    if level is not None:
        errors.extend(_validate_level(level))

    if "operation" in metadata:
        errors.extend(_validate_operation(metadata["operation"]))

    if "composes" in metadata:
        errors.extend(_validate_composes(metadata["composes"], level=level))

    return errors


def validate(skill_dir: Path) -> list[str]:
    """Validate a skill directory.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        List of validation error messages. Empty list means valid.
    """
    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        return [f"Path does not exist: {skill_dir}"]

    if not skill_dir.is_dir():
        return [f"Not a directory: {skill_dir}"]

    skill_md = find_skill_md(skill_dir)
    if skill_md is None:
        return ["Missing required file: SKILL.md"]

    try:
        content = skill_md.read_text()
        metadata, _ = parse_frontmatter(content)
    except ParseError as e:
        return [str(e)]

    return validate_metadata(metadata, skill_dir)
